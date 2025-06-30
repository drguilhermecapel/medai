# tests/integration/test_api_endpoints.py
"""
Testes de integração para endpoints da API MedAI.
Testa fluxos completos e integração entre componentes.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json
from typing import Dict

from app.main import app
from app.models import User, Patient, Exam, Diagnostic


class TestAuthEndpoints:
    """Testes para endpoints de autenticação."""
    
    def test_register_new_user(self, client: TestClient):
        """Testa registro de novo usuário."""
        user_data = {
            "email": "newdoctor@medai.com",
            "username": "drnew",
            "password": "SecurePass123!",
            "full_name": "Dr. New User",
            "role": "doctor",
            "specialization": "cardiology"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "password" not in data
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Testa login bem-sucedido."""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Testa login com credenciais inválidas."""
        login_data = {
            "username": "invalid@medai.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_refresh_token(self, client: TestClient, test_user: User):
        """Testa renovação de token."""
        # Primeiro faz login
        login_response = client.post("/api/v1/auth/login", data={
            "username": test_user.email,
            "password": "testpassword123"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Usa refresh token
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_protected_endpoint_without_auth(self, client: TestClient):
        """Testa acesso a endpoint protegido sem autenticação."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401


class TestPatientEndpoints:
    """Testes para endpoints de pacientes."""
    
    def test_create_patient(self, client: TestClient, auth_headers: Dict[str, str]):
        """Testa criação de paciente."""
        patient_data = {
            "name": "Maria Santos Silva",
            "cpf": "12345678909",
            "birth_date": "1985-06-15",
            "gender": "F",
            "phone": "(11) 98765-4321",
            "email": "maria.santos@email.com",
            "address": "Rua das Flores, 123",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01234-567",
            "medical_history": {
                "chronic_conditions": ["Asma"],
                "allergies": ["Dipirona"],
                "medications": []
            }
        }
        
        response = client.post(
            "/api/v1/patients",
            json=patient_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == patient_data["name"]
        assert data["cpf"] == patient_data["cpf"]
        assert "id" in data
    
    def test_get_patient(self, client: TestClient, test_patient: Patient, auth_headers: Dict[str, str]):
        """Testa busca de paciente por ID."""
        response = client.get(
            f"/api/v1/patients/{test_patient.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_patient.id
        assert data["name"] == test_patient.name
    
    def test_update_patient(self, client: TestClient, test_patient: Patient, auth_headers: Dict[str, str]):
        """Testa atualização de paciente."""
        update_data = {
            "phone": "(11) 99999-8888",
            "address": "Rua Nova, 456"
        }
        
        response = client.patch(
            f"/api/v1/patients/{test_patient.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == update_data["phone"]
        assert data["address"] == update_data["address"]
    
    def test_list_patients_with_filters(self, client: TestClient, auth_headers: Dict[str, str], db_session):
        """Testa listagem de pacientes com filtros."""
        # Cria múltiplos pacientes
        for i in range(5):
            patient = Patient(
                name=f"Patient {i}",
                cpf=f"1234567890{i}",
                birth_date=datetime(1990 + i, 1, 1),
                gender="M" if i % 2 == 0 else "F"
            )
            db_session.add(patient)
        db_session.commit()
        
        # Testa filtro por gênero
        response = client.get(
            "/api/v1/patients?gender=F&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 2
        assert all(p["gender"] == "F" for p in data["items"])
    
    def test_patient_medical_history(self, client: TestClient, test_patient: Patient, auth_headers: Dict[str, str]):
        """Testa histórico médico do paciente."""
        response = client.get(
            f"/api/v1/patients/{test_patient.id}/medical-history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "chronic_conditions" in data
        assert "Hipertensão" in data["chronic_conditions"]


class TestExamEndpoints:
    """Testes para endpoints de exames."""
    
    def test_create_exam(self, client: TestClient, test_patient: Patient, auth_headers: Dict[str, str]):
        """Testa criação de exame."""
        exam_data = {
            "patient_id": test_patient.id,
            "exam_type": "blood_test",
            "exam_date": datetime.now().isoformat(),
            "results": {
                "hemoglobin": 15.2,
                "glucose": 98,
                "cholesterol_total": 185
            },
            "notes": "Exame de rotina"
        }
        
        response = client.post(
            "/api/v1/exams",
            json=exam_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["exam_type"] == "blood_test"
        assert data["patient_id"] == test_patient.id
    
    def test_upload_exam_file(self, client: TestClient, test_exam: Exam, auth_headers: Dict[str, str]):
        """Testa upload de arquivo de exame."""
        # Simula arquivo PDF
        files = {
            "file": ("exam_result.pdf", b"PDF content here", "application/pdf")
        }
        
        response = client.post(
            f"/api/v1/exams/{test_exam.id}/upload",
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_url" in data
        assert data["file_type"] == "application/pdf"
    
    def test_analyze_exam_with_ai(self, client: TestClient, test_exam: Exam, auth_headers: Dict[str, str]):
        """Testa análise de exame com IA."""
        response = client.post(
            f"/api/v1/exams/{test_exam.id}/analyze",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "ai_analysis" in data
        assert "risk_factors" in data["ai_analysis"]
        assert "recommendations" in data["ai_analysis"]
        assert data["ai_analysis"]["confidence"] > 0.7
    
    def test_get_exam_history(self, client: TestClient, test_patient: Patient, auth_headers: Dict[str, str], db_session):
        """Testa histórico de exames do paciente."""
        # Cria múltiplos exames
        for i in range(3):
            exam = Exam(
                patient_id=test_patient.id,
                exam_type="blood_test",
                exam_date=datetime.now() - timedelta(days=30*i),
                results={"glucose": 95 + i*5}
            )
            db_session.add(exam)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/patients/{test_patient.id}/exams",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        # Verifica ordenação por data
        dates = [exam["exam_date"] for exam in data]
        assert dates == sorted(dates, reverse=True)


class TestDiagnosticEndpoints:
    """Testes para endpoints de diagnósticos."""
    
    def test_create_diagnostic(self, client: TestClient, test_patient: Patient, 
                             test_exam: Exam, auth_headers: Dict[str, str]):
        """Testa criação de diagnóstico."""
        diagnostic_data = {
            "patient_id": test_patient.id,
            "exam_id": test_exam.id,
            "diagnostic_text": "Quadro sugestivo de diabetes mellitus tipo 2",
            "icd10_codes": ["E11.9"],
            "severity": "moderate",
            "recommendations": [
                "Iniciar metformina 500mg 2x/dia",
                "Orientação nutricional",
                "Retorno em 30 dias"
            ]
        }
        
        response = client.post(
            "/api/v1/diagnostics",
            json=diagnostic_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == test_patient.id
        assert "E11.9" in data["icd10_codes"]
    
    def test_ai_assisted_diagnostic(self, client: TestClient, test_patient: Patient,
                                  test_exam: Exam, auth_headers: Dict[str, str]):
        """Testa diagnóstico assistido por IA."""
        ai_request = {
            "patient_id": test_patient.id,
            "exam_id": test_exam.id,
            "symptoms": ["sede excessiva", "perda de peso", "visão turva"],
            "use_ai": True
        }
        
        response = client.post(
            "/api/v1/diagnostics/ai-assist",
            json=ai_request,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "suggested_diagnosis" in data
        assert "confidence" in data
        assert "differential_diagnosis" in data
        assert len(data["differential_diagnosis"]) >= 2
    
    def test_generate_diagnostic_report(self, client: TestClient, test_diagnostic: Diagnostic,
                                      auth_headers: Dict[str, str]):
        """Testa geração de relatório de diagnóstico."""
        response = client.post(
            f"/api/v1/diagnostics/{test_diagnostic.id}/report",
            json={"format": "pdf", "include_exam_results": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 1000  # PDF tem conteúdo
    
    def test_diagnostic_follow_up(self, client: TestClient, test_diagnostic: Diagnostic,
                                 auth_headers: Dict[str, str]):
        """Testa acompanhamento de diagnóstico."""
        follow_up_data = {
            "notes": "Paciente apresentou melhora significativa",
            "status": "improving",
            "next_appointment": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(
            f"/api/v1/diagnostics/{test_diagnostic.id}/follow-up",
            json=follow_up_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "improving"


class TestHealthAndMonitoring:
    """Testes para endpoints de saúde e monitoramento."""
    
    def test_health_check(self, client: TestClient):
        """Testa endpoint de health check."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data["checks"]
        assert "ml_models" in data["checks"]
    
    def test_metrics_endpoint(self, client: TestClient, auth_headers: Dict[str, str]):
        """Testa endpoint de métricas."""
        response = client.get(
            "/api/v1/metrics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_patients" in data
        assert "total_exams" in data
        assert "total_diagnostics" in data
        assert "ml_model_accuracy" in data
    
    def test_system_logs(self, client: TestClient, auth_headers: Dict[str, str]):
        """Testa acesso aos logs do sistema (admin only)."""
        # Assume que auth_headers é de um admin
        response = client.get(
            "/api/v1/admin/logs?level=error&limit=50",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 403]  # 403 se não for admin


class TestCompleteWorkflow:
    """Testes de fluxo completo do sistema."""
    
    @pytest.mark.slow
    def test_complete_patient_journey(self, client: TestClient, auth_headers: Dict[str, str]):
        """Testa jornada completa do paciente: cadastro -> exame -> diagnóstico."""
        # 1. Cadastra paciente
        patient_response = client.post(
            "/api/v1/patients",
            json={
                "name": "Complete Journey Patient",
                "cpf": "98765432109",
                "birth_date": "1970-01-01",
                "gender": "M"
            },
            headers=auth_headers
        )
        assert patient_response.status_code == 201
        patient_id = patient_response.json()["id"]
        
        # 2. Cria exame
        exam_response = client.post(
            "/api/v1/exams",
            json={
                "patient_id": patient_id,
                "exam_type": "comprehensive_panel",
                "results": {
                    "glucose": 126,
                    "hba1c": 7.1,
                    "cholesterol_total": 220
                }
            },
            headers=auth_headers
        )
        assert exam_response.status_code == 201
        exam_id = exam_response.json()["id"]
        
        # 3. Analisa com IA
        analysis_response = client.post(
            f"/api/v1/exams/{exam_id}/analyze",
            headers=auth_headers
        )
        assert analysis_response.status_code == 200
        
        # 4. Cria diagnóstico
        diagnostic_response = client.post(
            "/api/v1/diagnostics",
            json={
                "patient_id": patient_id,
                "exam_id": exam_id,
                "diagnostic_text": "Diabetes mellitus tipo 2",
                "icd10_codes": ["E11.9"],
                "severity": "moderate"
            },
            headers=auth_headers
        )
        assert diagnostic_response.status_code == 201
        
        # 5. Gera relatório
        report_response = client.post(
            f"/api/v1/diagnostics/{diagnostic_response.json()['id']}/report",
            json={"format": "pdf"},
            headers=auth_headers
        )
        assert report_response.status_code == 200


class TestErrorHandling:
    """Testes para tratamento de erros."""
    
    def test_invalid_patient_data(self, client: TestClient, auth_headers: Dict[str, str]):
        """Testa validação de dados inválidos de paciente."""
        invalid_data = {
            "name": "A",  # Nome muito curto
            "cpf": "123",  # CPF inválido
            "birth_date": "2030-01-01",  # Data futura
            "gender": "X"  # Gênero inválido
        }
        
        response = client.post(
            "/api/v1/patients",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert len(errors) >= 4
    
    def test_duplicate_cpf(self, client: TestClient, test_patient: Patient, auth_headers: Dict[str, str]):
        """Testa erro de CPF duplicado."""
        duplicate_data = {
            "name": "Another Person",
            "cpf": test_patient.cpf,  # CPF já existe
            "birth_date": "1990-01-01",
            "gender": "M"
        }
        
        response = client.post(
            "/api/v1/patients",
            json=duplicate_data,
            headers=auth_headers
        )
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_resource_not_found(self, client: TestClient, auth_headers: Dict[str, str]):
        """Testa erro de recurso não encontrado."""
        response = client.get(
            "/api/v1/patients/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_insufficient_permissions(self, client: TestClient, db_session):
        """Testa erro de permissões insuficientes."""
        # Cria usuário com role limitado
        limited_user = User(
            email="nurse@medai.com",
            username="nurse",
            role="nurse",
            hashed_password="hashed"
        )
        db_session.add(limited_user)
        db_session.commit()
        
        # Gera token para nurse
        from app.security import create_access_token
        nurse_token = create_access_token({"sub": limited_user.email, "user_id": limited_user.id})
        nurse_headers = {"Authorization": f"Bearer {nurse_token}"}
        
        # Tenta acessar endpoint admin
        response = client.delete(
            "/api/v1/patients/1",
            headers=nurse_headers
        )
        
        assert response.status_code == 403
        assert "insufficient permissions" in response.json()["detail"].lower()