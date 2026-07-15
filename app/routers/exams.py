# -*- coding: utf-8 -*-
"""Rotas de exames."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Exam, Patient, User
from app.routers.auth import get_current_user
from app.schemas import ExamCreate, ExamResponse, ExamUpdate

router = APIRouter(prefix="/exams", tags=["Exames"])


def _get_exam_or_404(db: Session, exam_id: int) -> Exam:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exame não encontrado")
    return exam


@router.get("", response_model=List[ExamResponse])
def list_exams(
    patient_id: Optional[int] = None,
    exam_status: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista exames, com filtros por paciente e status."""
    query = db.query(Exam)
    if patient_id is not None:
        query = query.filter(Exam.patient_id == patient_id)
    if exam_status:
        query = query.filter(Exam.status == exam_status)
    return query.order_by(Exam.exam_date.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(
    payload: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registra um novo exame para um paciente."""
    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    data = payload.model_dump()
    if data.get("exam_date") is None:
        data["exam_date"] = datetime.utcnow()

    exam = Exam(**data, created_by_id=current_user.id)
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna um exame pelo ID."""
    return _get_exam_or_404(db, exam_id)


@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    payload: ExamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza um exame (resultados, status, etc.)."""
    exam = _get_exam_or_404(db, exam_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(exam, field, value)
    db.commit()
    db.refresh(exam)
    return exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove um exame."""
    exam = _get_exam_or_404(db, exam_id)
    db.delete(exam)
    db.commit()
