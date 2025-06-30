"""
Testes End-to-End abrangentes para o sistema MedAI
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json
import base64
import io
from PIL import Image
import numpy as np

from app.main import app
from app.core.database import Base, engine
from app.core.config import settings
from app.core.constants import UserRole, ExamType, ExamStatus, Priority


@pytest.fixture(scope="module")
def client():
    """Cliente de teste para E2E"""
    # Setup
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Teardown
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def admin_token(client):
    """Token de administrador para testes"""
    # Registra admin
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@medai.com",
            "username": "admin",
            "password": "Admin@123456",
            "full_name": "System Admin",
            "role": "admin"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@medai.com",
            "password": "Admin@123456"
        }
    )
    
    return response.json()["access_token"]


@pytest.fixture
def doctor_token(client):
    """Token de médico para testes"""
    # Registra médico
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "doctor@medai.com",
            "username": "doctor",
            "password": "Doctor@123456",
            "full_name": "Dr. House",
            "role": "doctor",
            "crm": "12345-SP"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "doctor@medai.com",
            "password": "Doctor@123456"
        }
    )
    
    return response.json()["access_token"]


@pytest.fixture
def patient_token(client):
    """Token de paciente para testes"""
    # Registra paciente
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "patient@medai.com",
            "username": "patient",
            "password": "Patient@123456",
            "full_name": "João Silva",
            "role": "patient",
            "cpf": "123.456.789-09",
            "date_of_birth": "1990-01-01",
            "phone": "(11) 98765-4321"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "patient@medai.com",
            "password": "Patient@123456"
        }
    )
    
    return response.json()["access_token"]


class TestCompletePatientJourney:
    """Testa a jornada completa do paciente no sistema"""
    
    def test_patient_registration_and_profile(self, client):
        """Testa registro e criação de perfil do paciente"""
        # 1. Registro
        register_data = {
            "email": "newpatient@example.com",
            "username": "newpatient",
            "password": "NewPatient@123456",
            "full_name": "Maria Santos",
            "role": "patient",
            "cpf": "987.654.321-00",
            "date_of_birth": "1985-05-15",
            "phone": "(11) 91234-5678",
            "gender": "female",
            "blood_type": "A+",
            "allergies": ["Penicilina", "Dipirona"],
            "medical_conditions": ["Hipertensão"],
            "emergency_contact": {
                "name": "José Santos",
                "phone": "(11) 98888-7777",
                "relationship": "Esposo"
            }
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        user_data = response.json()
        
        # 2. Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "newpatient@example.com",
                "password": "NewPatient@123456"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Visualizar perfil
        profile_response = client.get("/api/v1/patients/me", headers=headers)
        assert profile_response.status_code == 200
        profile = profile_response.json()
        
        assert profile["cpf"] == "987.654.321-00"
        assert profile["blood_type"] == "A+"
        assert len(profile["allergies"]) == 2
        
        # 4. Atualizar perfil
        update_data = {
            "address": "Rua das Flores, 123",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01234-567",
            "insurance_provider": "Unimed",
            "insurance_number": "123456789"
        }
        
        update_response = client.patch(
            "/api/v1/patients/me",
            headers=headers,
            json=update_data
        )
        assert update_response.status_code == 200
        
        # 5. Verificar atualização
        updated_profile = client.get("/api/v1/patients/me", headers=headers).json()
        assert updated_profile["address"] == "Rua das Flores, 123"
        assert updated_profile["insurance_provider"] == "Unimed"
    
    def test_patient_exam_request_flow(self, client, patient_token, doctor_token):
        """Testa fluxo de solicitação de exame pelo paciente"""
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # 1. Paciente solicita agendamento
        appointment_data = {
            "doctor_id": 2,  # ID do médico
            "preferred_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "reason": "Check-up anual",
            "symptoms": ["Dor de cabeça frequente", "Tontura"]
        }
        
        appointment_response = client.post(
            "/api/v1/appointments",
            headers=patient_headers,
            json=appointment_data
        )
        assert appointment_response.status_code == 201
        appointment_id = appointment_response.json()["id"]
        
        # 2. Médico aprova e solicita exames
        approval_response = client.patch(
            f"/api/v1/appointments/{appointment_id}/approve",
            headers=doctor_headers
        )
        assert approval_response.status_code == 200
        
        # Solicita exames
        exam_requests = [
            {
                "patient_id": 3,  # ID do paciente
                "exam_type": "blood_test",
                "priority": "medium",
                "notes": "Hemograma completo, glicemia, colesterol"
            },
            {
                "patient_id": 3,
                "exam_type": "ecg",
                "priority": "medium",
                "notes": "ECG de repouso"
            }
        ]
        
        exam_ids = []
        for exam_request in exam_requests:
            exam_response = client.post(
                "/api/v1/exams",
                headers=doctor_headers,
                json=exam_request
            )
            assert exam_response.status_code == 201
            exam_ids.append(exam_response.json()["id"])
        
        # 3. Paciente visualiza exames solicitados
        patient_exams = client.get(
            "/api/v1/exams/my-exams",
            headers=patient_headers
        ).json()
        
        assert len(patient_exams) >= 2
        assert all(exam["status"] == "pending" for exam in patient_exams)
        
        # 4. Paciente agenda realização dos exames
        for exam_id in exam_ids:
            schedule_response = client.post(
                f"/api/v1/exams/{exam_id}/schedule",
                headers=patient_headers,
                json={
                    "scheduled_date": (datetime.now() + timedelta(days=5)).isoformat(),
                    "location": "Laboratório Central"
                }
            )
            assert schedule_response.status_code == 200
    
    def test_patient_medical_history_access(self, client, patient_token):
        """Testa acesso do paciente ao histórico médico"""
        headers = {"Authorization": f"Bearer {patient_token}"}
        
        # 1. Visualizar histórico completo
        history_response = client.get(
            "/api/v1/patients/me/medical-history",
            headers=headers
        )
        assert history_response.status_code == 200
        history = history_response.json()
        
        # 2. Filtrar por período
        date_filter = {
            "start_date": (datetime.now() - timedelta(days=365)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        
        filtered_history = client.get(
            "/api/v1/patients/me/medical-history",
            headers=headers,
            params=date_filter
        ).json()
        
        # 3. Exportar histórico
        export_response = client.get(
            "/api/v1/patients/me/medical-history/export",
            headers=headers,
            params={"format": "pdf"}
        )
        assert export_response.status_code == 200
        assert export_response.headers["content-type"] == "application/pdf"
        
        # 4. Compartilhar com médico
        share_data = {
            "doctor_id": 2,
            "share_type": "full_history",
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        share_response = client.post(
            "/api/v1/patients/me/share-history",
            headers=headers,
            json=share_data
        )
        assert share_response.status_code == 201
        share_token = share_response.json()["share_token"]
        assert share_token is not None


class TestCompleteDoctorWorkflow:
    """Testa fluxo completo de trabalho do médico"""
    
    def test_doctor_patient_management(self, client, doctor_token):
        """Testa gerenciamento de pacientes pelo médico"""
        headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # 1. Listar pacientes
        patients_response = client.get(
            "/api/v1/doctors/patients",
            headers=headers
        )
        assert patients_response.status_code == 200
        patients = patients_response.json()
        
        # 2. Buscar paciente específico
        if patients:
            patient_id = patients[0]["id"]
            patient_detail = client.get(
                f"/api/v1/patients/{patient_id}",
                headers=headers
            ).json()
            
            assert patient_detail["id"] == patient_id
        
        # 3. Adicionar anotação ao prontuário
        clinical_note = {
            "patient_id": patient_id,
            "note_type": "consultation",
            "content": "Paciente apresenta melhora significativa...",
            "vital_signs": {
                "blood_pressure": "120/80",
                "heart_rate": 70,
                "temperature": 36.5,
                "respiratory_rate": 16,
                "oxygen_saturation": 98
            }
        }
        
        note_response = client.post(
            "/api/v1/clinical-notes",
            headers=headers,
            json=clinical_note
        )
        assert note_response.status_code == 201
        
        # 4. Prescrever medicamento
        prescription = {
            "patient_id": patient_id,
            "medications": [
                {
                    "name": "Paracetamol",
                    "dosage": "500mg",
                    "frequency": "6/6h",
                    "duration": "5 dias",
                    "instructions": "Tomar com água, após refeições"
                }
            ],
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        prescription_response = client.post(
            "/api/v1/prescriptions",
            headers=headers,
            json=prescription
        )
        assert prescription_response.status_code == 201
    
    def test_doctor_exam_analysis_workflow(self, client, doctor_token):
        """Testa fluxo de análise de exames pelo médico"""
        headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # 1. Listar exames pendentes de análise
        pending_exams = client.get(
            "/api/v1/exams/pending-analysis",
            headers=headers
        ).json()
        
        if pending_exams:
            exam_id = pending_exams[0]["id"]
            
            # 2. Visualizar detalhes do exame
            exam_detail = client.get(
                f"/api/v1/exams/{exam_id}",
                headers=headers
            ).json()
            
            # 3. Analisar resultados com IA
            ai_analysis_response = client.post(
                f"/api/v1/exams/{exam_id}/ai-analysis",
                headers=headers
            )
            assert ai_analysis_response.status_code == 200
            ai_results = ai_analysis_response.json()
            
            # 4. Criar diagnóstico
            diagnosis = {
                "exam_id": exam_id,
                "findings": ai_results.get("findings", []),
                "diagnosis": "Exame dentro dos padrões normais",
                "recommendations": [
                    "Manter acompanhamento regular",
                    "Repetir exame em 6 meses"
                ],
                "follow_up_required": True,
                "follow_up_date": (datetime.now() + timedelta(days=180)).isoformat()
            }
            
            diagnosis_response = client.post(
                "/api/v1/diagnostics",
                headers=headers,
                json=diagnosis
            )
            assert diagnosis_response.status_code == 201
            
            # 5. Notificar paciente
            notification = {
                "patient_id": exam_detail["patient_id"],
                "type": "exam_ready",
                "message": "Seu exame está pronto. Entre em contato para agendar retorno."
            }
            
            notify_response = client.post(
                "/api/v1/notifications",
                headers=headers,
                json=notification
            )
            assert notify_response.status_code == 201
    
    def test_doctor_statistics_dashboard(self, client, doctor_token):
        """Testa dashboard de estatísticas do médico"""
        headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # 1. Estatísticas gerais
        stats_response = client.get(
            "/api/v1/doctors/statistics",
            headers=headers
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        assert "total_patients" in stats
        assert "total_consultations" in stats
        assert "pending_exams" in stats
        assert "average_consultation_time" in stats
        
        # 2. Estatísticas por período
        period_stats = client.get(
            "/api/v1/doctors/statistics",
            headers=headers,
            params={
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat()
            }
        ).json()
        
        # 3. Relatório de produtividade
        productivity_report = client.get(
            "/api/v1/doctors/productivity-report",
            headers=headers,
            params={"month": datetime.now().month, "year": datetime.now().year}
        ).json()
        
        assert "consultations_per_day" in productivity_report
        assert "average_patients_per_day" in productivity_report


class TestCompleteAdminOperations:
    """Testa operações administrativas completas"""
    
    def test_admin_user_management(self, client, admin_token):
        """Testa gerenciamento de usuários pelo admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. Listar todos usuários
        users_response = client.get(
            "/api/v1/admin/users",
            headers=headers
        )
        assert users_response.status_code == 200
        users = users_response.json()
        
        # 2. Criar novo usuário (médico)
        new_doctor = {
            "email": "newdoctor@medai.com",
            "username": "newdoctor",
            "password": "TempPass@123",
            "full_name": "Dr. New Doctor",
            "role": "doctor",
            "crm": "98765-SP",
            "specialties": ["Cardiologia", "Clínica Geral"]
        }
        
        create_response = client.post(
            "/api/v1/admin/users",
            headers=headers,
            json=new_doctor
        )
        assert create_response.status_code == 201
        new_user_id = create_response.json()["id"]
        
        # 3. Atualizar permissões
        permissions_update = {
            "permissions": [
                "view_all_patients",
                "create_diagnosis",
                "prescribe_medication",
                "order_exams"
            ]
        }
        
        perm_response = client.patch(
            f"/api/v1/admin/users/{new_user_id}/permissions",
            headers=headers,
            json=permissions_update
        )
        assert perm_response.status_code == 200
        
        # 4. Suspender usuário
        suspend_response = client.patch(
            f"/api/v1/admin/users/{new_user_id}/suspend",
            headers=headers,
            json={"reason": "Documentação pendente"}
        )
        assert suspend_response.status_code == 200
        
        # 5. Reativar usuário
        reactivate_response = client.patch(
            f"/api/v1/admin/users/{new_user_id}/activate",
            headers=headers
        )
        assert reactivate_response.status_code == 200
    
    def test_admin_system_configuration(self, client, admin_token):
        """Testa configuração do sistema pelo admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. Configurações atuais
        config_response = client.get(
            "/api/v1/admin/system-config",
            headers=headers
        )
        assert config_response.status_code == 200
        current_config = config_response.json()
        
        # 2. Atualizar configurações
        new_config = {
            "appointment_duration_minutes": 30,
            "max_appointments_per_day": 20,
            "exam_result_retention_days": 365,
            "enable_ai_diagnostics": True,
            "ai_confidence_threshold": 0.85,
            "notification_settings": {
                "email_enabled": True,
                "sms_enabled": True,
                "push_enabled": True
            }
        }
        
        update_config_response = client.patch(
            "/api/v1/admin/system-config",
            headers=headers,
            json=new_config
        )
        assert update_config_response.status_code == 200
        
        # 3. Configurar integrações
        integration_config = {
            "laboratory_api": {
                "enabled": True,
                "endpoint": "https://lab.example.com/api",
                "api_key": "lab-api-key-123"
            },
            "pharmacy_integration": {
                "enabled": True,
                "provider": "FarmaciaPopular"
            }
        }
        
        integration_response = client.post(
            "/api/v1/admin/integrations",
            headers=headers,
            json=integration_config
        )
        assert integration_response.status_code == 201
    
    def test_admin_audit_and_compliance(self, client, admin_token):
        """Testa auditoria e compliance"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. Logs de auditoria
        audit_logs = client.get(
            "/api/v1/admin/audit-logs",
            headers=headers,
            params={
                "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
                "end_date": datetime.now().isoformat()
            }
        ).json()
        
        assert "logs" in audit_logs
        assert "total_count" in audit_logs
        
        # 2. Relatório de compliance LGPD
        lgpd_report = client.get(
            "/api/v1/admin/compliance/lgpd-report",
            headers=headers
        ).json()
        
        assert "data_subjects_count" in lgpd_report
        assert "data_processing_activities" in lgpd_report
        assert "consent_records" in lgpd_report
        
        # 3. Exportar dados para auditoria
        export_response = client.post(
            "/api/v1/admin/audit/export",
            headers=headers,
            json={
                "format": "csv",
                "include_pii": False,
                "date_range": {
                    "start": (datetime.now() - timedelta(days=30)).isoformat(),
                    "end": datetime.now().isoformat()
                }
            }
        )
        assert export_response.status_code == 200


class TestCompleteExamProcessing:
    """Testa processamento completo de diferentes tipos de exames"""
    
    def test_ecg_exam_complete_flow(self, client, patient_token, doctor_token):
        """Testa fluxo completo de exame ECG"""
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # 1. Médico solicita ECG
        exam_request = {
            "patient_id": 3,
            "exam_type": "ecg",
            "priority": "high",
            "notes": "Paciente com palpitações",
            "clinical_indication": "Investigação de arritmia"
        }
        
        exam_response = client.post(
            "/api/v1/exams",
            headers=doctor_headers,
            json=exam_request
        )
        assert exam_response.status_code == 201
        exam_id = exam_response.json()["id"]
        
        # 2. Técnico realiza o exame (simula upload de dados)
        ecg_data = {
            "heart_rate": 75,
            "pr_interval": 160,
            "qrs_duration": 100,
            "qt_interval": 400,
            "rhythm": "sinus",
            "leads": {
                "I": np.random.randn(5000).tolist(),
                "II": np.random.randn(5000).tolist(),
                "III": np.random.randn(5000).tolist(),
                "aVR": np.random.randn(5000).tolist(),
                "aVL": np.random.randn(5000).tolist(),
                "aVF": np.random.randn(5000).tolist(),
                "V1": np.random.randn(5000).tolist(),
                "V2": np.random.randn(5000).tolist(),
                "V3": np.random.randn(5000).tolist(),
                "V4": np.random.randn(5000).tolist(),
                "V5": np.random.randn(5000).tolist(),
                "V6": np.random.randn(5000).tolist()
            }
        }
        
        # Técnico faz login
        tech_token = client.post(
            "/api/v1/auth/login",
            data={
                "username": "tech@medai.com",
                "password": "Tech@123456"
            }
        ).json().get("access_token")
        
        tech_headers = {"Authorization": f"Bearer {tech_token}"}
        
        upload_response = client.post(
            f"/api/v1/exams/{exam_id}/upload-results",
            headers=tech_headers,
            json=ecg_data
        )
        assert upload_response.status_code == 200
        
        # 3. Sistema processa com IA
        ai_process_response = client.post(
            f"/api/v1/exams/{exam_id}/process-ai",
            headers=tech_headers
        )
        assert ai_process_response.status_code == 200
        ai_results = ai_process_response.json()
        
        # 4. Médico revisa resultados
        review_response = client.get(
            f"/api/v1/exams/{exam_id}/ai-results",
            headers=doctor_headers
        )
        assert review_response.status_code == 200
        
        # 5. Médico finaliza diagnóstico
        final_diagnosis = {
            "exam_id": exam_id,
            "ai_findings": ai_results.get("findings", []),
            "doctor_assessment": "ECG normal, ritmo sinusal regular",
            "diagnosis_code": "Z00.00",  # CID-10
            "recommendations": [
                "ECG dentro dos padrões normais",
                "Manter acompanhamento clínico"
            ]
        }
        
        diagnosis_response = client.post(
            "/api/v1/diagnostics",
            headers=doctor_headers,
            json=final_diagnosis
        )
        assert diagnosis_response.status_code == 201
        
        # 6. Paciente acessa resultado
        patient_result = client.get(
            f"/api/v1/exams/{exam_id}/result",
            headers=patient_headers
        ).json()
        
        assert patient_result["status"] == "completed"
        assert "diagnosis" in patient_result
    
    def test_blood_test_complete_flow(self, client, patient_token, doctor_token):
        """Testa fluxo completo de exame de sangue"""
        doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # 1. Solicitar exame de sangue completo
        exam_request = {
            "patient_id": 3,
            "exam_type": "blood_test",
            "priority": "medium",
            "tests_requested": [
                "hemograma_completo",
                "glicemia",
                "colesterol_total",
                "hdl",
                "ldl",
                "triglicerides",
                "creatinina",
                "ureia",
                "ast",
                "alt"
            ]
        }
        
        exam_response = client.post(
            "/api/v1/exams",
            headers=doctor_headers,
            json=exam_request
        )
        assert exam_response.status_code == 201
        exam_id = exam_response.json()["id"]
        
        # 2. Laboratório envia resultados
        lab_results = {
            "hemoglobin": 14.5,
            "hematocrit": 42.0,
            "red_cells": 4.8,
            "white_cells": 7500,
            "platelets": 250000,
            "glucose": 92,
            "cholesterol_total": 180,
            "hdl": 55,
            "ldl": 100,
            "triglycerides": 125,
            "creatinine": 0.9,
            "urea": 35,
            "ast": 25,
            "alt": 30
        }
        
        # Simula integração com laboratório
        lab_upload_response = client.post(
            f"/api/v1/exams/{exam_id}/lab-results",
            headers={"X-API-Key": "lab-integration-key"},
            json={
                "lab_id": "LAB123",
                "results": lab_results,
                "collection_date": datetime.now().isoformat(),
                "validation_date": datetime.now().isoformat()
            }
        )
        assert lab_upload_response.status_code == 200
        
        # 3. Sistema analisa valores de referência
        analysis_response = client.get(
            f"/api/v1/exams/{exam_id}/reference-analysis",
            headers=doctor_headers
        ).json()
        
        assert "normal_values" in analysis_response
        assert "alerts" in analysis_response
    
    def test_imaging_exam_flow(self, client, patient_token, doctor_token):
        """Testa fluxo de exame de imagem"""
        doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # 1. Solicitar raio-X
        exam_request = {
            "patient_id": 3,
            "exam_type": "xray",
            "priority": "high",
            "body_region": "chest",
            "clinical_indication": "Suspeita de pneumonia",
            "contrast_required": False
        }
        
        exam_response = client.post(
            "/api/v1/exams",
            headers=doctor_headers,
            json=exam_request
        )
        assert exam_response.status_code == 201
        exam_id = exam_response.json()["id"]
        
        # 2. Upload de imagem DICOM (simulado)
        # Cria imagem fake para teste
        img = Image.new('L', (512, 512), color=128)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        image_upload = {
            "exam_id": exam_id,
            "images": [{
                "filename": "chest_pa.dcm",
                "data": img_base64,
                "metadata": {
                    "study_date": datetime.now().isoformat(),
                    "modality": "CR",
                    "body_part": "CHEST",
                    "view_position": "PA"
                }
            }]
        }
        
        tech_token = "tech_token"  # Assumindo token do técnico
        tech_headers = {"Authorization": f"Bearer {tech_token}"}
        
        upload_response = client.post(
            f"/api/v1/exams/{exam_id}/upload-images",
            headers=tech_headers,
            json=image_upload
        )
        assert upload_response.status_code == 200
        
        # 3. Análise por IA de imagem
        ai_image_analysis = client.post(
            f"/api/v1/exams/{exam_id}/analyze-image",
            headers=doctor_headers
        ).json()
        
        assert "findings" in ai_image_analysis
        assert "confidence_scores" in ai_image_analysis


class TestSystemIntegrations:
    """Testa integrações do sistema"""
    
    @patch('app.services.email_service.EmailService.send_email')
    def test_notification_system(self, mock_email, client, patient_token, doctor_token):
        """Testa sistema de notificações"""
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # 1. Configurar preferências de notificação
        preferences = {
            "email_notifications": True,
            "sms_notifications": True,
            "push_notifications": False,
            "notification_types": {
                "exam_ready": True,
                "appointment_reminder": True,
                "prescription_reminder": True,
                "health_tips": False
            }
        }
        
        pref_response = client.patch(
            "/api/v1/users/notification-preferences",
            headers=patient_headers,
            json=preferences
        )
        assert pref_response.status_code == 200
        
        # 2. Trigger de notificação (exame pronto)
        # Simula conclusão de exame
        exam_complete_notification = {
            "user_id": 3,
            "type": "exam_ready",
            "title": "Exame Disponível",
            "message": "Seu exame de sangue está pronto para visualização",
            "action_url": "/exams/123/result"
        }
        
        # Verifica se email foi enviado
        assert mock_email.called
    
    def test_appointment_scheduling_system(self, client, patient_token, doctor_token):
        """Testa sistema de agendamento"""
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        
        # 1. Buscar horários disponíveis
        availability_response = client.get(
            "/api/v1/appointments/availability",
            headers=patient_headers,
            params={
                "doctor_id": 2,
                "date": (datetime.now() + timedelta(days=7)).date().isoformat(),
                "duration_minutes": 30
            }
        )
        assert availability_response.status_code == 200
        available_slots = availability_response.json()
        
        # 2. Agendar consulta
        if available_slots:
            appointment_data = {
                "doctor_id": 2,
                "datetime": available_slots[0]["datetime"],
                "duration_minutes": 30,
                "type": "consultation",
                "reason": "Consulta de rotina"
            }
            
            booking_response = client.post(
                "/api/v1/appointments",
                headers=patient_headers,
                json=appointment_data
            )
            assert booking_response.status_code == 201
            appointment_id = booking_response.json()["id"]
            
            # 3. Reagendar
            new_datetime = datetime.now() + timedelta(days=10, hours=14)
            reschedule_response = client.patch(
                f"/api/v1/appointments/{appointment_id}/reschedule",
                headers=patient_headers,
                json={"new_datetime": new_datetime.isoformat()}
            )
            assert reschedule_response.status_code == 200
            
            # 4. Cancelar
            cancel_response = client.delete(
                f"/api/v1/appointments/{appointment_id}",
                headers=patient_headers,
                json={"reason": "Motivo pessoal"}
            )
            assert cancel_response.status_code == 200
    
    def test_billing_integration(self, client, admin_token):
        """Testa integração com sistema de faturamento"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. Gerar fatura para paciente
        billing_data = {
            "patient_id": 3,
            "items": [
                {
                    "type": "consultation",
                    "description": "Consulta médica",
                    "quantity": 1,
                    "unit_price": 150.00
                },
                {
                    "type": "exam",
                    "description": "Hemograma completo",
                    "quantity": 1,
                    "unit_price": 45.00
                },
                {
                    "type": "exam",
                    "description": "ECG",
                    "quantity": 1,
                    "unit_price": 80.00
                }
            ],
            "insurance_coverage": {
                "provider": "Unimed",
                "coverage_percentage": 70,
                "authorization_number": "AUTH123456"
            }
        }
        
        invoice_response = client.post(
            "/api/v1/billing/invoices",
            headers=headers,
            json=billing_data
        )
        assert invoice_response.status_code == 201
        invoice = invoice_response.json()
        
        assert invoice["total_amount"] == 275.00
        assert invoice["insurance_covered"] == 192.50
        assert invoice["patient_amount"] == 82.50
        
        # 2. Processar pagamento
        payment_data = {
            "invoice_id": invoice["id"],
            "payment_method": "credit_card",
            "amount": 82.50,
            "installments": 1
        }
        
        payment_response = client.post(
            "/api/v1/billing/payments",
            headers=headers,
            json=payment_data
        )
        assert payment_response.status_code == 200


class TestSecurityAndCompliance:
    """Testa segurança e compliance do sistema"""
    
    def test_data_privacy_lgpd(self, client, patient_token):
        """Testa compliance com LGPD"""
        headers = {"Authorization": f"Bearer {patient_token}"}
        
        # 1. Solicitar todos os dados pessoais
        data_request = client.get(
            "/api/v1/privacy/my-data",
            headers=headers
        )
        assert data_request.status_code == 200
        personal_data = data_request.json()
        
        assert "personal_info" in personal_data
        assert "medical_records" in personal_data
        assert "exam_history" in personal_data
        
        # 2. Baixar dados em formato portável
        download_response = client.get(
            "/api/v1/privacy/download-my-data",
            headers=headers,
            params={"format": "json"}
        )
        assert download_response.status_code == 200
        
        # 3. Revogar consentimento específico
        consent_revoke = {
            "consent_type": "marketing_communications",
            "revoked": True
        }
        
        revoke_response = client.patch(
            "/api/v1/privacy/consent",
            headers=headers,
            json=consent_revoke
        )
        assert revoke_response.status_code == 200
        
        # 4. Solicitar exclusão de dados
        deletion_request = {
            "reason": "Não desejo mais usar o serviço",
            "confirm_email": "patient@medai.com",
            "delete_medical_records": False  # Manter por obrigação legal
        }
        
        deletion_response = client.post(
            "/api/v1/privacy/request-deletion",
            headers=headers,
            json=deletion_request
        )
        assert deletion_response.status_code == 202  # Accepted for processing
    
    def test_access_control_rbac(self, client, patient_token, doctor_token, admin_token):
        """Testa controle de acesso baseado em papéis"""
        # Endpoints que só admin pode acessar
        admin_only_endpoints = [
            ("/api/v1/admin/users", "GET"),
            ("/api/v1/admin/system-config", "GET"),
            ("/api/v1/admin/audit-logs", "GET")
        ]
        
        for endpoint, method in admin_only_endpoints:
            # Paciente não deve ter acesso
            patient_response = client.request(
                method,
                endpoint,
                headers={"Authorization": f"Bearer {patient_token}"}
            )
            assert patient_response.status_code == 403
            
            # Admin deve ter acesso
            admin_response = client.request(
                method,
                endpoint,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert admin_response.status_code in [200, 201]
        
        # Endpoints médico-específicos
        doctor_endpoints = [
            ("/api/v1/diagnostics", "POST"),
            ("/api/v1/prescriptions", "POST")
        ]
        
        for endpoint, method in doctor_endpoints:
            # Paciente não deve poder criar
            if method == "POST":
                patient_response = client.request(
                    method,
                    endpoint,
                    headers={"Authorization": f"Bearer {patient_token}"},
                    json={}
                )
                assert patient_response.status_code == 403
    
    def test_audit_trail(self, client, admin_token):
        """Testa trilha de auditoria"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Realizar ações que devem ser auditadas
        actions = [
            ("POST", "/api/v1/users", {"email": "audit@test.com", "password": "Test@123"}),
            ("GET", "/api/v1/patients/1", {}),
            ("POST", "/api/v1/exams", {"patient_id": 1, "exam_type": "ecg"})
        ]
        
        for method, endpoint, data in actions:
            client.request(method, endpoint, headers=headers, json=data if data else None)
        
        # Verificar logs de auditoria
        audit_logs = client.get(
            "/api/v1/admin/audit-logs",
            headers=headers,
            params={
                "user_id": 1,
                "limit": 10
            }
        ).json()
        
        assert len(audit_logs["logs"]) >= 3
        
        # Verificar informações do log
        for log in audit_logs["logs"]:
            assert "timestamp" in log
            assert "user_id" in log
            assert "action" in log
            assert "resource" in log
            assert "ip_address" in log


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=term-missing"])