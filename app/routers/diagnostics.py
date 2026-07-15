# -*- coding: utf-8 -*-
"""Rotas de diagnósticos."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Diagnostic, Exam, Patient, User
from app.routers.auth import get_current_user
from app.schemas import DiagnosticCreate, DiagnosticResponse
from app.services.diagnostic_service import DiagnosticService

router = APIRouter(prefix="/diagnostics", tags=["Diagnósticos"])

diagnostic_service = DiagnosticService()


def _get_diagnostic_or_404(db: Session, diagnostic_id: int) -> Diagnostic:
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnóstico não encontrado")
    return diagnostic


@router.get("", response_model=List[DiagnosticResponse])
def list_diagnostics(
    patient_id: Optional[int] = None,
    severity: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista diagnósticos, com filtros por paciente e severidade."""
    query = db.query(Diagnostic)
    if patient_id is not None:
        query = query.filter(Diagnostic.patient_id == patient_id)
    if severity:
        query = query.filter(Diagnostic.severity == severity)
    return query.order_by(Diagnostic.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=DiagnosticResponse, status_code=status.HTTP_201_CREATED)
def create_diagnostic(
    payload: DiagnosticCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registra um diagnóstico para um paciente."""
    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    if payload.exam_id is not None:
        exam = db.query(Exam).filter(Exam.id == payload.exam_id).first()
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exame não encontrado")

    diagnostic = Diagnostic(**payload.model_dump(), created_by_id=current_user.id)
    db.add(diagnostic)
    db.commit()
    db.refresh(diagnostic)
    return diagnostic


@router.get("/{diagnostic_id}", response_model=DiagnosticResponse)
def get_diagnostic(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna um diagnóstico pelo ID."""
    return _get_diagnostic_or_404(db, diagnostic_id)


@router.post("/analyze/{exam_id}", response_model=DiagnosticResponse, status_code=status.HTTP_201_CREATED)
def analyze_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analisa os resultados de um exame contra os valores de referência e gera um diagnóstico."""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exame não encontrado")
    if not exam.results:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Exame sem resultados para analisar")

    analysis = diagnostic_service.analyze_exam_results(exam.results, exam.reference_values)

    if analysis["abnormal_count"] == 0:
        text = "Todos os parâmetros analisados estão dentro dos valores de referência."
    else:
        altered = ", ".join(f["parameter"] for f in analysis["findings"])
        text = f"Análise automática: {analysis['abnormal_count']} parâmetro(s) fora da referência ({altered})."

    diagnostic = Diagnostic(
        patient_id=exam.patient_id,
        exam_id=exam.id,
        diagnostic_text=text,
        ai_analysis=analysis,
        severity=analysis["severity"],
        created_by_id=current_user.id,
    )
    db.add(diagnostic)
    db.commit()
    db.refresh(diagnostic)
    return diagnostic


@router.delete("/{diagnostic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diagnostic(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove um diagnóstico."""
    diagnostic = _get_diagnostic_or_404(db, diagnostic_id)
    db.delete(diagnostic)
    db.commit()
