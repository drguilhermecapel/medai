"""
Testes de integração para o sistema MedAI
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.models.patient import Patient
from app.models.exam import Exam
from app.models.diagnostic import Diagnostic
from app.services.user_service import UserService
from app.services.patient_service import PatientService
from app.services.exam_service import ExamService
from app.services.diagnostic_service import DiagnosticService
from app.services.ml_model_service import MLModelService
from app.services.notification_service import NotificationService
from app.repositories.user_repository import UserRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.exam_repository import ExamRepository
from app.core.constants import UserRole, ExamType, ExamStatus, DiagnosticStatus, Priority


# Configuração do banco de testes
TEST_DATABASE_URL = "sqlite:///./test_medai.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Sessão de banco de dados para testes"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user_service(db_session):
    """Serviço de usuário para testes"""
    return UserService(db_session)


@pytest.fixture
def patient_service(db_session):
    """Serviço de paciente para testes"""
    return PatientService(db_session)


@pytest.fixture
def exam_service(db_session):
    """Serviço de exame para testes"""
    return ExamService(db_session)


@pytest.fixture
def diagnostic_service(db_session):
    """Serviço de diagnóstico para testes"""
    return DiagnosticService(db_session)


@pytest.fixture
def ml_service():
    """Serviço de ML para testes"""
    return MLModelService()


class TestUserPatientIntegration:
    """Testes de integração entre usuários e pacientes"""
    
    async def test_create_patient_user(self, user_service, patient_service):
        """Testa criação de usuário paciente"""
        # Cria usuário
        user_data = {
            "email": "patient@example.com",
            "username": "patient123",
            "password": "Patient@123456",
            "full_name": "João Silva",
            "role": UserRole.PATIENT
        }
        
        user = await user_service.create_user(user_data)
        assert user.id is not None
        assert user.role == UserRole.PATIENT
        
        # Cria perfil de paciente
        patient_data = {
            "user_id": user.id,
            "cpf": "123.456.789-09",
            "date_of_birth": "1990-01-01",
            "phone": "(11) 98765-4321",
            "address": "Rua Teste, 123",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01234-567",
            "blood_type": "O+",
            "allergies": ["Dipirona"],
            "medical_history": "Hipertensão"
        }
        
        patient = await patient_service.create_patient(patient_data)
        assert patient.id is not None
        assert patient.user_id == user.id
        assert patient.cpf == "123.456.789-09"
        
        # Verifica relacionamento
        retrieved_patient = await patient_service.get_by_user_id(user.id)
        assert retrieved_patient is not None
        assert retrieved_patient.user.email == "patient@example.com"
    
    async def test_multiple_roles_integration(self, user_service):
        """Testa integração com múltiplos papéis de usuário"""
        roles = [UserRole.DOCTOR, UserRole.NURSE, UserRole.TECHNICIAN, UserRole.ADMIN]
        
        for i, role in enumerate(roles):
            user_data = {
                "email": f"{role.value}@example.com",
                "username": f"{role.value}_user",
                "password": "Test@123456",
                "full_name": f"Test {role.value.title()}",
                "role": role
            }
            
            user = await user_service.create_user(user_data)
            assert user.role == role
            
            # Verifica permissões específicas do papel
            if role == UserRole.ADMIN:
                assert await user_service.has_permission(user.id, "manage_users")
            elif role == UserRole.DOCTOR:
                assert await user_service.has_permission(user.id, "create_diagnosis")
            elif role == UserRole.NURSE:
                assert await user_service.has_permission(user.id, "update_patient_vitals")
            elif role == UserRole.TECHNICIAN:
                assert await user_service.has_permission(user.id, "upload_exam_results")


class TestExamWorkflow:
    """Testes do fluxo completo de exames"""
    
    async def test_complete_ecg_exam_workflow(
        self,
        user_service,
        patient_service,
        exam_service,
        diagnostic_service,
        ml_service
    ):
        """Testa fluxo completo de exame ECG"""
        # 1. Cria médico e paciente
        doctor = await user_service.create_user({
            "email": "doctor@example.com",
            "username": "doctor",
            "password": "Doctor@123456",
            "full_name": "Dr. Silva",
            "role": UserRole.DOCTOR
        })
        
        patient_user = await user_service.create_user({
            "email": "patient@example.com",
            "username": "patient",
            "password": "Patient@123456",
            "full_name": "João Costa",
            "role": UserRole.PATIENT
        })
        
        patient = await patient_service.create_patient({
            "user_id": patient_user.id,
            "cpf": "987.654.321-00",
            "date_of_birth": "1985-05-15"
        })
        
        # 2. Cria solicitação de exame
        exam_request = {
            "patient_id": patient.id,
            "doctor_id": doctor.id,
            "exam_type": ExamType.ECG,
            "priority": Priority.MEDIUM,
            "notes": "Paciente com palpitações",
            "requested_at": datetime.utcnow()
        }
        
        exam = await exam_service.create_exam(exam_request)
        assert exam.status == ExamStatus.PENDING
        
        # 3. Técnico realiza o exame
        technician = await user_service.create_user({
            "email": "tech@example.com",
            "username": "technician",
            "password": "Tech@123456",
            "full_name": "Carlos Tech",
            "role": UserRole.TECHNICIAN
        })
        
        # Atualiza status para em progresso
        await exam_service.update_status(
            exam.id,
            ExamStatus.IN_PROGRESS,
            technician.id
        )
        
        # 4. Upload dos dados do ECG
        ecg_data = {
            "heart_rate": 75,
            "pr_interval": 160,
            "qrs_duration": 100,
            "qt_interval": 400,
            "raw_data": np.random.randn(5000).tolist()
        }
        
        await exam_service.upload_exam_data(
            exam.id,
            ecg_data,
            technician.id
        )
        
        # Marca como completo
        await exam_service.update_status(
            exam.id,
            ExamStatus.COMPLETED,
            technician.id
        )
        
        # 5. Processamento por IA
        # Treina modelo mock para teste
        train_data = pd.DataFrame({
            'heart_rate': np.random.randint(60, 100, 100),
            'pr_interval': np.random.randint(120, 200, 100),
            'qrs_duration': np.random.randint(80, 120, 100),
            'qt_interval': np.random.randint(350, 450, 100),
            'diagnosis': np.random.choice(['normal', 'arritmia'], 100)
        })
        
        ml_service.train_model(
            train_data,
            'diagnosis',
            ExamType.ECG,
            'ecg_classifier'
        )
        
        # Cria diagnóstico automático
        features = {
            'heart_rate': ecg_data['heart_rate'],
            'pr_interval': ecg_data['pr_interval'],
            'qrs_duration': ecg_data['qrs_duration'],
            'qt_interval': ecg_data['qt_interval']
        }
        
        prediction = ml_service.predict('ecg_classifier', ExamType.ECG, features)
        
        diagnostic = await diagnostic_service.create_diagnostic({
            "exam_id": exam.id,
            "doctor_id": doctor.id,
            "ai_prediction": prediction.prediction,
            "ai_confidence": prediction.confidence,
            "status": DiagnosticStatus.PENDING
        })
        
        # 6. Médico revisa e finaliza diagnóstico
        await diagnostic_service.update_diagnostic(
            diagnostic.id,
            {
                "diagnosis": "Ritmo sinusal normal",
                "recommendations": "Manter acompanhamento regular",
                "status": DiagnosticStatus.REVIEWED
            },
            doctor.id
        )
        
        # Verifica fluxo completo
        final_exam = await exam_service.get_exam(exam.id)
        assert final_exam.status == ExamStatus.COMPLETED
        
        final_diagnostic = await diagnostic_service.get_by_exam_id(exam.id)
        assert final_diagnostic.status == DiagnosticStatus.REVIEWED
        assert final_diagnostic.ai_prediction is not None
    
    async def test_blood_test_workflow_with_alerts(
        self,
        user_service,
        patient_service,
        exam_service,
        diagnostic_service
    ):
        """Testa fluxo de exame de sangue com alertas"""
        # Cria usuários necessários
        doctor = await user_service.create_user({
            "email": "dr.blood@example.com",
            "username": "drblood",
            "password": "Doctor@123456",
            "full_name": "Dr. Blood",
            "role": UserRole.DOCTOR
        })
        
        patient_user = await user_service.create_user({
            "email": "patient.blood@example.com",
            "username": "patientblood",
            "password": "Patient@123456",
            "full_name": "Maria Santos",
            "role": UserRole.PATIENT
        })
        
        patient = await patient_service.create_patient({
            "user_id": patient_user.id,
            "cpf": "111.222.333-44",
            "date_of_birth": "1970-03-20",
            "gender": "female"
        })
        
        # Cria exame
        exam = await exam_service.create_exam({
            "patient_id": patient.id,
            "doctor_id": doctor.id,
            "exam_type": ExamType.BLOOD_TEST,
            "priority": Priority.HIGH,
            "notes": "Check-up anual"
        })
        
        # Resultados com valores alterados
        blood_results = {
            "hemoglobin": 10.5,      # Baixo para mulher
            "glucose": 150,          # Alto
            "cholesterol_total": 250, # Alto
            "hdl": 35,              # Baixo
            "ldl": 160,             # Alto
            "triglycerides": 200     # Alto
        }
        
        await exam_service.upload_exam_data(exam.id, blood_results, doctor.id)
        
        # Processa alertas
        alerts = await diagnostic_service.process_blood_test_alerts(
            blood_results,
            patient.gender,
            patient.age
        )
        
        assert len(alerts) > 0
        assert any(alert['parameter'] == 'hemoglobin' for alert in alerts)
        assert any(alert['parameter'] == 'glucose' for alert in alerts)
        
        # Cria diagnóstico com alertas
        diagnostic = await diagnostic_service.create_diagnostic({
            "exam_id": exam.id,
            "doctor_id": doctor.id,
            "alerts": alerts,
            "priority": Priority.HIGH,
            "status": DiagnosticStatus.PROCESSING
        })
        
        # Verifica se notificação foi criada para valores críticos
        critical_params = ['hemoglobin', 'glucose']
        has_critical = any(
            alert['parameter'] in critical_params 
            for alert in alerts
        )
        
        if has_critical:
            assert diagnostic.priority == Priority.HIGH


class TestNotificationIntegration:
    """Testes de integração do sistema de notificações"""
    
    @patch('app.services.email_service.EmailService.send_email')
    @patch('app.services.sms_service.SMSService.send_sms')
    async def test_exam_ready_notification(
        self,
        mock_sms,
        mock_email,
        user_service,
        patient_service,
        exam_service,
        notification_service
    ):
        """Testa notificação quando exame fica pronto"""
        # Setup
        patient_user = await user_service.create_user({
            "email": "patient.notify@example.com",
            "username": "patientnotify",
            "password": "Patient@123456",
            "full_name": "Ana Costa",
            "role": UserRole.PATIENT,
            "notification_preferences": {
                "email": True,
                "sms": True,
                "exam_ready": True
            }
        })
        
        patient = await patient_service.create_patient({
            "user_id": patient_user.id,
            "cpf": "555.666.777-88",
            "phone": "(11) 98765-4321"
        })
        
        # Cria e completa exame
        exam = await exam_service.create_exam({
            "patient_id": patient.id,
            "exam_type": ExamType.XRAY,
            "priority": Priority.MEDIUM
        })
        
        # Marca como completo (deve disparar notificação)
        await exam_service.update_status(
            exam.id,
            ExamStatus.COMPLETED,
            user_id=1  # ID do técnico
        )
        
        # Verifica se notificações foram enviadas
        await asyncio.sleep(0.1)  # Aguarda processamento assíncrono
        
        mock_email.assert_called_once()
        email_call = mock_email.call_args
        assert patient_user.email in str(email_call)
        assert "exame" in str(email_call).lower()
        
        mock_sms.assert_called_once()
        sms_call = mock_sms.call_args
        assert patient.phone in str(sms_call)
    
    async def test_critical_result_notification(
        self,
        user_service,
        patient_service,
        exam_service,
        diagnostic_service,
        notification_service
    ):
        """Testa notificação para resultados críticos"""
        # Cria médico e paciente
        doctor = await user_service.create_user({
            "email": "doctor.critical@example.com",
            "username": "drcritical",
            "password": "Doctor@123456",
            "full_name": "Dr. Critical",
            "role": UserRole.DOCTOR,
            "notification_preferences": {
                "critical_results": True,
                "push": True
            }
        })
        
        patient_user = await user_service.create_user({
            "email": "patient.critical@example.com",
            "username": "patientcritical",
            "password": "Patient@123456",
            "full_name": "Pedro Critical",
            "role": UserRole.PATIENT
        })
        
        patient = await patient_service.create_patient({
            "user_id": patient_user.id,
            "cpf": "999.888.777-66"
        })
        
        # Cria exame com resultado crítico
        exam = await exam_service.create_exam({
            "patient_id": patient.id,
            "doctor_id": doctor.id,
            "exam_type": ExamType.BLOOD_TEST,
            "priority": Priority.CRITICAL
        })
        
        # Resultado crítico
        critical_results = {
            "glucose": 300,  # Muito alto - crítico
            "hemoglobin": 7.0  # Muito baixo - crítico
        }
        
        await exam_service.upload_exam_data(exam.id, critical_results, doctor.id)
        
        # Cria diagnóstico crítico
        diagnostic = await diagnostic_service.create_diagnostic({
            "exam_id": exam.id,
            "doctor_id": doctor.id,
            "diagnosis": "Valores críticos detectados",
            "priority": Priority.CRITICAL,
            "is_critical": True
        })
        
        # Verifica se notificação urgente foi criada
        notifications = await notification_service.get_pending_notifications(doctor.id)
        
        critical_notifications = [
            n for n in notifications 
            if n.priority == Priority.CRITICAL
        ]
        
        assert len(critical_notifications) > 0
        assert any("crítico" in n.message.lower() for n in critical_notifications)


class TestDataConsistency:
    """Testes de consistência de dados"""
    
    async def test_cascade_deletion(self, user_service, patient_service, exam_service):
        """Testa deleção em cascata"""
        # Cria estrutura completa
        user = await user_service.create_user({
            "email": "cascade@example.com",
            "username": "cascade",
            "password": "Cascade@123456",
            "full_name": "Test Cascade",
            "role": UserRole.PATIENT
        })
        
        patient = await patient_service.create_patient({
            "user_id": user.id,
            "cpf": "777.888.999-00"
        })
        
        exam = await exam_service.create_exam({
            "patient_id": patient.id,
            "exam_type": ExamType.ECG
        })
        
        # Deleta usuário (deve deletar tudo em cascata)
        await user_service.delete_user(user.id)
        
        # Verifica se tudo foi deletado
        assert await user_service.get_user(user.id) is None
        assert await patient_service.get_patient(patient.id) is None
        assert await exam_service.get_exam(exam.id) is None
    
    async def test_transaction_rollback(self, user_service, db_session):
        """Testa rollback de transação em caso de erro"""
        initial_count = await user_service.count_users()
        
        try:
            async with db_session.begin():
                # Cria usuário válido
                await user_service.create_user({
                    "email": "rollback1@example.com",
                    "username": "rollback1",
                    "password": "Test@123456",
                    "full_name": "Test Rollback 1"
                })
                
                # Tenta criar usuário com email duplicado (deve falhar)
                await user_service.create_user({
                    "email": "rollback1@example.com",  # Duplicado
                    "username": "rollback2",
                    "password": "Test@123456",
                    "full_name": "Test Rollback 2"
                })
        except Exception:
            pass  # Esperado
        
        # Verifica que nenhum usuário foi criado
        final_count = await user_service.count_users()
        assert final_count == initial_count
    
    async def test_concurrent_updates(self, exam_service, patient_service):
        """Testa atualizações concorrentes"""
        # Cria paciente e exame
        patient = await patient_service.create_patient({
            "cpf": "123.123.123-12"
        })
        
        exam = await exam_service.create_exam({
            "patient_id": patient.id,
            "exam_type": ExamType.BLOOD_TEST
        })
        
        # Simula atualizações concorrentes
        tasks = []
        for i in range(5):
            task = exam_service.update_exam(
                exam.id,
                {"notes": f"Update {i}"}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verifica que pelo menos uma atualização teve sucesso
        successful_updates = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_updates) >= 1
        
        # Verifica estado final
        final_exam = await exam_service.get_exam(exam.id)
        assert final_exam.notes is not None
        assert "Update" in final_exam.notes


class TestPerformanceIntegration:
    """Testes de performance e otimização"""
    
    async def test_bulk_patient_creation(self, patient_service):
        """Testa criação em massa de pacientes"""
        start_time = datetime.utcnow()
        
        patients_data = []
        for i in range(100):
            patients_data.append({
                "cpf": f"{i:011d}",
                "date_of_birth": "1990-01-01",
                "full_name": f"Patient {i}"
            })
        
        # Criação em lote
        patients = await patient_service.bulk_create(patients_data)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        assert len(patients) == 100
        assert duration < 5  # Deve completar em menos de 5 segundos
    
    async def test_query_optimization(self, patient_service, exam_service):
        """Testa otimização de queries"""
        # Cria dados de teste
        patient = await patient_service.create_patient({
            "cpf": "optimization-test"
        })
        
        # Cria múltiplos exames
        for i in range(20):
            await exam_service.create_exam({
                "patient_id": patient.id,
                "exam_type": ExamType.BLOOD_TEST
            })
        
        # Query otimizada com eager loading
        patient_with_exams = await patient_service.get_patient_with_exams(
            patient.id
        )
        
        # Verifica que todos os exames foram carregados
        assert len(patient_with_exams.exams) == 20
        
        # Acesso aos exames não deve gerar novas queries
        for exam in patient_with_exams.exams:
            assert exam.patient_id == patient.id
    
    async def test_cache_effectiveness(self, user_service):
        """Testa efetividade do cache"""
        # Cria usuário
        user = await user_service.create_user({
            "email": "cache@example.com",
            "username": "cacheuser",
            "password": "Cache@123456",
            "full_name": "Cache Test"
        })
        
        # Primeira busca (sem cache)
        start1 = datetime.utcnow()
        user1 = await user_service.get_user(user.id)
        time1 = (datetime.utcnow() - start1).total_seconds()
        
        # Segunda busca (com cache)
        start2 = datetime.utcnow()
        user2 = await user_service.get_user(user.id)
        time2 = (datetime.utcnow() - start2).total_seconds()
        
        # Cache deve ser mais rápido
        assert time2 < time1
        assert user1.id == user2.id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=term-missing"])