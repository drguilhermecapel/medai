"""
Testes abrangentes para o serviço de validação
"""
import pytest
import numpy as np
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock
import os
import tempfile

from app.services.validation_service import ValidationService
from app.core.constants import Gender, ExamType


class TestValidationServiceCPF:
    """Testes para validação de CPF"""
    
    def test_valid_cpf_with_formatting(self):
        """Testa CPF válido com formatação"""
        valid_cpfs = [
            "123.456.789-09",
            "111.444.777-35",
            "000.000.001-91"
        ]
        
        for cpf in valid_cpfs:
            assert ValidationService.validate_cpf(cpf) is True
    
    def test_valid_cpf_without_formatting(self):
        """Testa CPF válido sem formatação"""
        valid_cpfs = [
            "12345678909",
            "11144477735",
            "00000000191"
        ]
        
        for cpf in valid_cpfs:
            assert ValidationService.validate_cpf(cpf) is True
    
    def test_invalid_cpf(self):
        """Testa CPF inválido"""
        invalid_cpfs = [
            "123.456.789-00",  # Dígito verificador errado
            "111.111.111-11",  # Todos dígitos iguais
            "999.999.999-99",  # Todos dígitos iguais
            "123.456.789",     # Formato incompleto
            "12345678901234",  # Muitos dígitos
            "abcd.efgh.ijk",   # Letras
            ""                 # Vazio
        ]
        
        for cpf in invalid_cpfs:
            assert ValidationService.validate_cpf(cpf) is False
    
    def test_cpf_edge_cases(self):
        """Testa casos extremos de CPF"""
        # CPF com zeros à esquerda
        assert ValidationService.validate_cpf("000.000.001-91") is True
        assert ValidationService.validate_cpf("00000000191") is True
        
        # CPF nulo/None
        assert ValidationService.validate_cpf(None) is False
        
        # CPF com caracteres especiais extras
        assert ValidationService.validate_cpf("123.456.789-09!") is False


class TestValidationServiceContact:
    """Testes para validação de contatos"""
    
    def test_valid_phone_numbers(self):
        """Testa números de telefone válidos"""
        valid_phones = [
            "+55 11 98765-4321",
            "+5511987654321",
            "(11) 98765-4321",
            "11 98765-4321",
            "11987654321",
            "(11) 3456-7890",
            "11 3456-7890",
            "1134567890"
        ]
        
        for phone in valid_phones:
            assert ValidationService.validate_phone(phone) is True
    
    def test_invalid_phone_numbers(self):
        """Testa números de telefone inválidos"""
        invalid_phones = [
            "123",              # Muito curto
            "abcd-efgh",        # Letras
            "11 98765-43",      # Incompleto
            "(11) 98765-43210", # Muitos dígitos
            ""                  # Vazio
        ]
        
        for phone in invalid_phones:
            assert ValidationService.validate_phone(phone) is False
    
    def test_valid_emails(self):
        """Testa emails válidos"""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com",
            "first.last@company.org"
        ]
        
        for email in valid_emails:
            assert ValidationService.validate_email(email) is True
    
    def test_invalid_emails(self):
        """Testa emails inválidos"""
        invalid_emails = [
            "user@",
            "@example.com",
            "user@.com",
            "user example@com",
            "user@example",
            "",
            "user@"
        ]
        
        for email in invalid_emails:
            assert ValidationService.validate_email(email) is False
    
    def test_email_case_insensitive(self):
        """Testa que validação de email é case-insensitive"""
        assert ValidationService.validate_email("User@Example.COM") is True
        assert ValidationService.validate_email("USER@EXAMPLE.COM") is True


class TestValidationServiceDates:
    """Testes para validação de datas"""
    
    def test_valid_date_of_birth(self):
        """Testa data de nascimento válida"""
        today = date.today()
        
        valid_dates = [
            today - timedelta(days=365*25),  # 25 anos atrás
            today - timedelta(days=365*50),  # 50 anos atrás
            today - timedelta(days=1),       # Ontem
            date(1950, 1, 1),                # Data fixa antiga
            date(2000, 12, 31)               # Virada do milênio
        ]
        
        for dob in valid_dates:
            valid, message = ValidationService.validate_date_of_birth(dob)
            assert valid is True
            assert message is None
    
    def test_invalid_date_of_birth(self):
        """Testa data de nascimento inválida"""
        today = date.today()
        
        # Data no futuro
        future_date = today + timedelta(days=1)
        valid, message = ValidationService.validate_date_of_birth(future_date)
        assert valid is False
        assert "futuro" in message.lower()
        
        # Idade muito alta
        very_old = today - timedelta(days=365*151)
        valid, message = ValidationService.validate_date_of_birth(very_old)
        assert valid is False
        assert "150" in message
    
    def test_edge_case_dates(self):
        """Testa casos extremos de data"""
        today = date.today()
        
        # Nascido hoje
        valid, message = ValidationService.validate_date_of_birth(today)
        assert valid is True
        
        # Exatamente 150 anos
        exactly_150 = today - timedelta(days=365*150)
        valid, message = ValidationService.validate_date_of_birth(exactly_150)
        assert valid is True


class TestValidationServiceBloodTests:
    """Testes para validação de exames de sangue"""
    
    def test_normal_blood_test_results(self):
        """Testa resultados normais de exame de sangue"""
        normal_results = {
            'hemoglobin': 15.0,
            'hematocrit': 45.0,
            'red_cells': 5.0,
            'white_cells': 7.0,
            'platelets': 250.0,
            'glucose': 90.0,
            'cholesterol_total': 180.0,
            'hdl': 50.0,
            'ldl': 100.0,
            'triglycerides': 120.0
        }
        
        validation = ValidationService.validate_blood_test_results(
            normal_results,
            Gender.MALE,
            30
        )
        
        assert validation['valid'] is True
        assert validation['has_alerts'] is False
        assert len(validation['alerts']) == 0
    
    def test_abnormal_blood_test_results(self):
        """Testa resultados anormais de exame de sangue"""
        abnormal_results = {
            'hemoglobin': 10.0,      # Baixo
            'glucose': 150.0,        # Alto
            'cholesterol_total': 250.0,  # Alto
            'hdl': 30.0,            # Baixo para homem
            'triglycerides': 300.0   # Alto
        }
        
        validation = ValidationService.validate_blood_test_results(
            abnormal_results,
            Gender.MALE,
            40
        )
        
        assert validation['valid'] is True  # Ainda válido, mas com alertas
        assert validation['has_alerts'] is True
        assert len(validation['alerts']) > 0
        
        # Verifica alertas específicos
        alert_params = [alert['parameter'] for alert in validation['alerts']]
        assert 'hemoglobin' in alert_params
        assert 'glucose' in alert_params
        assert 'cholesterol_total' in alert_params
    
    def test_gender_specific_ranges(self):
        """Testa faixas específicas por gênero"""
        # Hemoglobina no limite inferior feminino, mas baixo para masculino
        results = {'hemoglobin': 12.5}
        
        # Para mulher - normal
        validation_female = ValidationService.validate_blood_test_results(
            results,
            Gender.FEMALE,
            30
        )
        assert validation_female['results']['hemoglobin']['status'] == 'normal'
        
        # Para homem - baixo
        validation_male = ValidationService.validate_blood_test_results(
            results,
            Gender.MALE,
            30
        )
        assert validation_male['results']['hemoglobin']['status'] == 'low'
    
    def test_missing_parameters(self):
        """Testa com parâmetros faltantes"""
        partial_results = {
            'hemoglobin': 14.0,
            'glucose': 95.0
            # Outros parâmetros omitidos
        }
        
        validation = ValidationService.validate_blood_test_results(
            partial_results,
            Gender.OTHER
        )
        
        assert validation['valid'] is True
        assert len(validation['results']) == 2
    
    def test_extreme_values(self):
        """Testa valores extremos"""
        extreme_results = {
            'hemoglobin': 5.0,       # Muito baixo
            'glucose': 500.0,        # Muito alto
            'platelets': 50.0,       # Muito baixo
            'white_cells': 30.0      # Muito alto
        }
        
        validation = ValidationService.validate_blood_test_results(
            extreme_results
        )
        
        assert validation['has_alerts'] is True
        assert len(validation['alerts']) == len(extreme_results)


class TestValidationServiceVitalSigns:
    """Testes para validação de sinais vitais"""
    
    def test_adult_normal_vital_signs(self):
        """Testa sinais vitais normais de adulto"""
        vital_signs = {
            'heart_rate': 70,
            'respiratory_rate': 16,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'temperature': 36.8,
            'oxygen_saturation': 98
        }
        
        validation = ValidationService.validate_vital_signs(vital_signs, 30)
        
        assert validation['valid'] is True
        assert validation['has_alerts'] is False
        assert validation['age_category'] == 'adult'
    
    def test_age_specific_ranges(self):
        """Testa faixas específicas por idade"""
        # Frequência cardíaca de 140 - normal para bebê, alta para adulto
        vital_signs = {'heart_rate': 130}
        
        # Para bebê
        validation_infant = ValidationService.validate_vital_signs(vital_signs, 0.5)
        assert validation_infant['results']['heart_rate']['status'] == 'normal'
        assert validation_infant['age_category'] == 'infant'
        
        # Para adulto
        validation_adult = ValidationService.validate_vital_signs(vital_signs, 30)
        assert validation_adult['results']['heart_rate']['status'] == 'high'
        assert validation_adult['age_category'] == 'adult'
    
    def test_all_age_categories(self):
        """Testa todas as categorias de idade"""
        vital_signs = {'heart_rate': 80}
        
        age_categories = [
            (0.01, 'newborn'),      # Recém-nascido
            (0.5, 'infant'),        # Bebê
            (5, 'child'),           # Criança
            (15, 'teenager'),       # Adolescente
            (30, 'adult'),          # Adulto
            (70, 'elderly')         # Idoso
        ]
        
        for age, expected_category in age_categories:
            validation = ValidationService.validate_vital_signs(vital_signs, age)
            assert validation['age_category'] == expected_category
    
    def test_critical_vital_signs(self):
        """Testa sinais vitais críticos"""
        critical_signs = {
            'heart_rate': 200,              # Taquicardia severa
            'respiratory_rate': 40,          # Taquipneia
            'blood_pressure_systolic': 200,  # Hipertensão severa
            'blood_pressure_diastolic': 120, # Hipertensão severa
            'temperature': 40.0,            # Febre alta
            'oxygen_saturation': 85         # Hipóxia
        }
        
        validation = ValidationService.validate_vital_signs(critical_signs, 40)
        
        assert validation['has_alerts'] is True
        assert len(validation['alerts']) == len(critical_signs)


class TestValidationServiceECG:
    """Testes para validação de dados de ECG"""
    
    def test_normal_ecg_data(self):
        """Testa dados normais de ECG"""
        ecg_data = {
            'heart_rate': 70,
            'pr_interval': 160,
            'qrs_duration': 100,
            'qt_interval': 400,
            'raw_data': np.random.randn(5000).tolist()  # 10s @ 500Hz
        }
        
        validation = ValidationService.validate_ecg_data(ecg_data)
        
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
        assert len(validation['warnings']) == 0
    
    def test_abnormal_heart_rate(self):
        """Testa frequência cardíaca anormal"""
        # Bradicardia
        ecg_data_low = {'heart_rate': 35}
        validation_low = ValidationService.validate_ecg_data(ecg_data_low)
        assert len(validation_low['warnings']) > 0
        assert "baixa" in validation_low['warnings'][0].lower()
        
        # Taquicardia
        ecg_data_high = {'heart_rate': 220}
        validation_high = ValidationService.validate_ecg_data(ecg_data_high)
        assert len(validation_high['warnings']) > 0
        assert "alta" in validation_high['warnings'][0].lower()
    
    def test_raw_data_validation(self):
        """Testa validação de dados brutos"""
        # Número incorreto de amostras
        ecg_data_wrong_samples = {
            'raw_data': np.random.randn(3000).tolist()  # Apenas 6s
        }
        validation = ValidationService.validate_ecg_data(ecg_data_wrong_samples)
        assert validation['valid'] is False
        assert len(validation['errors']) > 0
        
        # Dados com NaN
        ecg_data_nan = {
            'raw_data': [float('nan')] * 5000
        }
        validation_nan = ValidationService.validate_ecg_data(ecg_data_nan)
        assert validation_nan['valid'] is False
        assert "NaN" in str(validation_nan['errors'])
        
        # Dados com infinito
        ecg_data_inf = {
            'raw_data': [float('inf')] * 5000
        }
        validation_inf = ValidationService.validate_ecg_data(ecg_data_inf)
        assert validation_inf['valid'] is False
        assert "infinito" in str(validation_inf['errors'])
    
    def test_multi_lead_ecg(self):
        """Testa ECG de múltiplas derivações"""
        leads = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 
                'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
        
        # Dados corretos
        ecg_data_correct = {
            'raw_data': np.random.randn(12, 5000)  # 12 leads x 5000 samples
        }
        validation = ValidationService.validate_ecg_data(ecg_data_correct, leads)
        assert validation['valid'] is True
        
        # Número incorreto de derivações
        ecg_data_wrong_leads = {
            'raw_data': np.random.randn(10, 5000)  # Apenas 10 leads
        }
        validation_wrong = ValidationService.validate_ecg_data(ecg_data_wrong_leads, leads)
        assert validation_wrong['valid'] is False
        assert "derivações" in str(validation_wrong['errors'])
    
    def test_ecg_intervals(self):
        """Testa validação de intervalos ECG"""
        # Intervalos anormais
        ecg_data_abnormal_intervals = {
            'pr_interval': 250,      # Prolongado
            'qrs_duration': 140,     # Alargado
            'qt_interval': 500       # Prolongado
        }
        
        validation = ValidationService.validate_ecg_data(ecg_data_abnormal_intervals)
        assert len(validation['warnings']) >= 3
        
        # Verifica mensagens específicas
        warning_text = ' '.join(validation['warnings'])
        assert 'pr_interval' in warning_text
        assert 'qrs_duration' in warning_text
        assert 'qt_interval' in warning_text
    
    def test_ecg_amplitude_validation(self):
        """Testa validação de amplitude"""
        # Amplitude muito alta
        high_amplitude_data = np.random.randn(5000) * 10  # Amplitude alta
        ecg_data = {'raw_data': high_amplitude_data.tolist()}
        
        validation = ValidationService.validate_ecg_data(ecg_data)
        assert len(validation['warnings']) > 0
        assert "amplitude" in validation['warnings'][0].lower()


class TestValidationServiceMedication:
    """Testes para validação de medicamentos"""
    
    def test_valid_medication_dosage(self):
        """Testa dosagem válida de medicamento"""
        validation = ValidationService.validate_medication_dosage(
            medication="Paracetamol",
            dosage=500,
            unit="mg",
            weight=70,
            age=30
        )
        
        assert validation['valid'] is True
        assert len(validation['warnings']) == 0
    
    def test_invalid_unit(self):
        """Testa unidade inválida"""
        validation = ValidationService.validate_medication_dosage(
            medication="Test Drug",
            dosage=100,
            unit="xyz"  # Unidade inválida
        )
        
        assert validation['valid'] is False
        assert len(validation['warnings']) > 0
        assert "unidade" in validation['warnings'][0].lower()
    
    def test_weight_based_dosage(self):
        """Testa dosagem baseada em peso"""
        validation = ValidationService.validate_medication_dosage(
            medication="Antibiótico",
            dosage=10,
            unit="mg/kg",
            weight=50
        )
        
        assert validation['valid'] is True
        assert len(validation['recommendations']) > 0
        assert "500" in validation['recommendations'][0]  # Dose total
    
    def test_age_based_recommendations(self):
        """Testa recomendações baseadas em idade"""
        # Criança
        validation_child = ValidationService.validate_medication_dosage(
            medication="Medicine",
            dosage=100,
            unit="mg",
            age=8
        )
        assert any("pediátrica" in rec for rec in validation_child['recommendations'])
        
        # Idoso
        validation_elderly = ValidationService.validate_medication_dosage(
            medication="Medicine",
            dosage=100,
            unit="mg",
            age=75
        )
        assert any("idosos" in rec for rec in validation_elderly['recommendations'])


class TestValidationServiceImageFiles:
    """Testes para validação de arquivos de imagem"""
    
    def test_valid_image_file(self):
        """Testa arquivo de imagem válido"""
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(b'fake image data')
            tmp_path = tmp.name
        
        try:
            validation = ValidationService.validate_image_file(
                tmp_path,
                ExamType.XRAY
            )
            
            assert validation['valid'] is True
            assert 'size_mb' in validation['metadata']
        finally:
            os.unlink(tmp_path)
    
    def test_non_existent_file(self):
        """Testa arquivo não existente"""
        validation = ValidationService.validate_image_file(
            "/path/to/nonexistent/file.jpg",
            ExamType.XRAY
        )
        
        assert validation['valid'] is False
        assert len(validation['errors']) > 0
        assert "não encontrado" in validation['errors'][0]
    
    def test_invalid_extension_warning(self):
        """Testa aviso de extensão inválida"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'not an image')
            tmp_path = tmp.name
        
        try:
            validation = ValidationService.validate_image_file(
                tmp_path,
                ExamType.XRAY
            )
            
            assert validation['valid'] is True  # Ainda válido, mas com aviso
            assert len(validation['warnings']) > 0
            assert ".txt" in validation['warnings'][0]
        finally:
            os.unlink(tmp_path)
    
    def test_large_file_warning(self):
        """Testa aviso de arquivo grande"""
        with tempfile.NamedTemporaryFile(suffix='.dcm', delete=False) as tmp:
            # Cria arquivo de 101 MB
            tmp.write(b'0' * (101 * 1024 * 1024))
            tmp_path = tmp.name
        
        try:
            validation = ValidationService.validate_image_file(
                tmp_path,
                ExamType.CT_SCAN
            )
            
            assert len(validation['warnings']) > 0
            assert "grande" in validation['warnings'][0].lower()
            assert validation['metadata']['size_mb'] > 100
        finally:
            os.unlink(tmp_path)
    
    @patch('pydicom.dcmread')
    def test_dicom_file_validation(self, mock_dcmread):
        """Testa validação de arquivo DICOM"""
        # Mock do dataset DICOM
        mock_ds = MagicMock()
        mock_ds.get.side_effect = lambda key, default='': {
            'Modality': 'CT',
            'StudyDate': '20240101',
            'PatientID': '12345'
        }.get(key, default)
        mock_dcmread.return_value = mock_ds
        
        with tempfile.NamedTemporaryFile(suffix='.dcm', delete=False) as tmp:
            tmp.write(b'DICOM data')
            tmp_path = tmp.name
        
        try:
            validation = ValidationService.validate_image_file(
                tmp_path,
                ExamType.CT_SCAN
            )
            
            assert validation['valid'] is True
            assert validation['metadata']['modality'] == 'CT'
            assert validation['metadata']['study_date'] == '20240101'
            assert validation['metadata']['patient_id'] == '12345'
        finally:
            os.unlink(tmp_path)


class TestValidationServiceLabReport:
    """Testes para validação de relatório laboratorial"""
    
    def test_valid_lab_report(self):
        """Testa relatório laboratorial válido"""
        report_data = {
            'patient_id': '12345',
            'exam_date': datetime.now().isoformat(),
            'exam_type': 'blood_test',
            'results': {
                'hemoglobin': 14.5,
                'glucose': 92.0
            }
        }
        
        validation = ValidationService.validate_lab_report(report_data)
        
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
    
    def test_missing_required_fields(self):
        """Testa campos obrigatórios faltantes"""
        incomplete_report = {
            'patient_id': '12345',
            # exam_date faltando
            'exam_type': 'blood_test'
            # results faltando
        }
        
        validation = ValidationService.validate_lab_report(incomplete_report)
        
        assert validation['valid'] is False
        assert len(validation['errors']) >= 2
        assert any('exam_date' in error for error in validation['errors'])
        assert any('results' in error for error in validation['errors'])
    
    def test_future_exam_date(self):
        """Testa data de exame no futuro"""
        future_date = datetime.now() + timedelta(days=1)
        
        report_data = {
            'patient_id': '12345',
            'exam_date': future_date.isoformat(),
            'exam_type': 'blood_test',
            'results': {}
        }
        
        validation = ValidationService.validate_lab_report(report_data)
        
        assert validation['valid'] is False
        assert any('futuro' in error for error in validation['errors'])
    
    def test_blood_test_validation_integration(self):
        """Testa integração com validação de exame de sangue"""
        report_data = {
            'patient_id': '12345',
            'exam_date': datetime.now().isoformat(),
            'exam_type': 'blood_test',
            'patient_gender': 'male',
            'patient_age': 35,
            'results': {
                'hemoglobin': 10.0,  # Baixo
                'glucose': 150.0     # Alto
            }
        }
        
        validation = ValidationService.validate_lab_report(report_data)
        
        assert 'blood_test' in validation['sections']
        blood_validation = validation['sections']['blood_test']
        assert blood_validation['has_alerts'] is True
        assert len(validation['warnings']) > 0


class TestValidationServiceBMI:
    """Testes para cálculo de IMC"""
    
    def test_bmi_calculation(self):
        """Testa cálculo básico de IMC"""
        result = ValidationService.calculate_bmi(weight=70, height=1.75)
        
        expected_bmi = 70 / (1.75 ** 2)
        assert result['bmi'] == round(expected_bmi, 2)
        assert result['weight'] == 70
        assert result['height'] == 1.75
    
    def test_bmi_classifications(self):
        """Testa todas as classificações de IMC"""
        test_cases = [
            (50, 1.75, "Abaixo do peso"),      # IMC ~16.3
            (65, 1.75, "Peso normal"),          # IMC ~21.2
            (85, 1.75, "Sobrepeso"),            # IMC ~27.8
            (100, 1.75, "Obesidade grau I"),    # IMC ~32.7
            (115, 1.75, "Obesidade grau II"),   # IMC ~37.6
            (130, 1.75, "Obesidade grau III")   # IMC ~42.4
        ]
        
        for weight, height, expected_class in test_cases:
            result = ValidationService.calculate_bmi(weight, height)
            assert result['classification'] == expected_class
    
    def test_bmi_edge_cases(self):
        """Testa casos extremos de IMC"""
        # Valores limítrofes
        test_cases = [
            (56.65, 1.75),  # IMC ~18.5 (limite inferior peso normal)
            (76.56, 1.75),  # IMC ~25.0 (limite superior peso normal)
            (91.87, 1.75),  # IMC ~30.0 (limite obesidade)
        ]
        
        for weight, height in test_cases:
            result = ValidationService.calculate_bmi(weight, height)
            assert isinstance(result['bmi'], float)
            assert result['bmi'] > 0


class TestValidationServicePatientData:
    """Testes para validação de dados do paciente"""
    
    def test_complete_valid_patient_data(self):
        """Testa dados completos e válidos do paciente"""
        patient_data = {
            'cpf': '123.456.789-09',
            'email': 'patient@example.com',
            'phone': '(11) 98765-4321',
            'date_of_birth': '1990-01-01',
            'weight': 70,
            'height': 1.75
        }
        
        validation = ValidationService.validate_patient_data(patient_data)
        
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
        assert validation['fields']['cpf'] == 'valid'
        assert validation['fields']['email'] == 'valid'
        assert validation['fields']['phone'] == 'valid'
        assert validation['fields']['date_of_birth'] == 'valid'
        assert 'bmi' in validation['fields']
    
    def test_partial_patient_data(self):
        """Testa dados parciais do paciente"""
        patient_data = {
            'email': 'patient@example.com',
            'phone': '(11) 98765-4321'
        }
        
        validation = ValidationService.validate_patient_data(patient_data)
        
        assert validation['valid'] is True
        assert validation['fields']['email'] == 'valid'
        assert validation['fields']['phone'] == 'valid'
        assert 'cpf' not in validation['fields']
    
    def test_invalid_patient_data(self):
        """Testa dados inválidos do paciente"""
        patient_data = {
            'cpf': '123.456.789-00',  # Inválido
            'email': 'invalid-email',  # Inválido
            'phone': '123',            # Formato incorreto
            'date_of_birth': '2030-01-01'  # Futuro
        }
        
        validation = ValidationService.validate_patient_data(patient_data)
        
        assert validation['valid'] is False
        assert len(validation['errors']) > 0
        assert validation['fields']['cpf'] == 'invalid'
        assert validation['fields']['email'] == 'invalid'
        assert validation['fields']['phone'] == 'warning'
        assert validation['fields']['date_of_birth'] == 'invalid'
    
    def test_patient_data_with_invalid_date_format(self):
        """Testa formato de data inválido"""
        patient_data = {
            'date_of_birth': '01/01/1990'  # Formato incorreto
        }
        
        validation = ValidationService.validate_patient_data(patient_data)
        
        assert validation['valid'] is False
        assert validation['fields']['date_of_birth'] == 'invalid'
        assert any('formato' in error.lower() for error in validation['errors'])
    
    def test_patient_data_bmi_calculation_error(self):
        """Testa erro no cálculo de IMC"""
        patient_data = {
            'weight': 70,
            'height': 0  # Altura zero causará erro
        }
        
        validation = ValidationService.validate_patient_data(patient_data)
        
        assert 'bmi' not in validation['fields']
        assert any('IMC' in warning for warning in validation['warnings'])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.services.validation_service", "--cov-report=term-missing"])