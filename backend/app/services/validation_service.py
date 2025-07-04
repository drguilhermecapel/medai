"""
Serviço de validação de dados médicos
"""
import re
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
import logging

from backend.app.core.constants import (
    Gender,
    ExamType,
    MIN_HEART_RATE,
    MAX_HEART_RATE,
    ECG_SAMPLE_RATE,
    ECG_DURATION,
    ECG_LEADS
)

logger = logging.getLogger(__name__)


class ValidationService:
    """Serviço para validação de dados médicos"""
    
    # Padrões de validação
    CPF_PATTERN = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$')
    PHONE_PATTERN = re.compile(r'^(\+\d{1,3})?\s?\(?\d{2,3}\)?\s?\d{4,5}-?\d{4}$')
    EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    
    # Faixas de referência para exames de sangue
    BLOOD_REFERENCE_RANGES = {
        'hemoglobin': {
            'male': (13.5, 17.5),     # g/dL
            'female': (12.0, 15.5),    # g/dL
            'unit': 'g/dL'
        },
        'hematocrit': {
            'male': (39, 50),          # %
            'female': (35, 45),        # %
            'unit': '%'
        },
        'red_cells': {
            'male': (4.5, 6.0),        # milhões/mm³
            'female': (4.0, 5.5),      # milhões/mm³
            'unit': 'milhões/mm³'
        },
        'white_cells': {
            'all': (4.0, 11.0),        # mil/mm³
            'unit': 'mil/mm³'
        },
        'platelets': {
            'all': (150, 400),         # mil/mm³
            'unit': 'mil/mm³'
        },
        'glucose': {
            'fasting': (70, 99),       # mg/dL
            'postprandial': (70, 140), # mg/dL
            'unit': 'mg/dL'
        },
        'cholesterol_total': {
            'desirable': (0, 200),     # mg/dL
            'borderline': (200, 239),  # mg/dL
            'high': (240, float('inf')), # mg/dL
            'unit': 'mg/dL'
        },
        'hdl': {
            'male': (40, float('inf')), # mg/dL
            'female': (50, float('inf')), # mg/dL
            'unit': 'mg/dL'
        },
        'ldl': {
            'optimal': (0, 100),       # mg/dL
            'near_optimal': (100, 129), # mg/dL
            'borderline': (130, 159),  # mg/dL
            'high': (160, 189),        # mg/dL
            'very_high': (190, float('inf')), # mg/dL
            'unit': 'mg/dL'
        },
        'triglycerides': {
            'normal': (0, 150),        # mg/dL
            'borderline': (150, 199),  # mg/dL
            'high': (200, 499),        # mg/dL
            'very_high': (500, float('inf')), # mg/dL
            'unit': 'mg/dL'
        },
        'creatinine': {
            'male': (0.7, 1.3),        # mg/dL
            'female': (0.6, 1.1),      # mg/dL
            'unit': 'mg/dL'
        },
        'urea': {
            'all': (10, 50),           # mg/dL
            'unit': 'mg/dL'
        },
        'ast': {
            'all': (10, 40),           # U/L
            'unit': 'U/L'
        },
        'alt': {
            'all': (10, 40),           # U/L
            'unit': 'U/L'
        }
    }
    
    # Faixas normais de sinais vitais por idade
    VITAL_SIGNS_RANGES = {
        'heart_rate': {
            'newborn': (120, 160),
            'infant': (80, 140),
            'child': (75, 120),
            'teenager': (60, 100),
            'adult': (60, 100),
            'elderly': (60, 100)
        },
        'respiratory_rate': {
            'newborn': (30, 60),
            'infant': (24, 40),
            'child': (18, 30),
            'teenager': (12, 20),
            'adult': (12, 20),
            'elderly': (12, 20)
        },
        'blood_pressure_systolic': {
            'newborn': (60, 90),
            'infant': (80, 100),
            'child': (90, 110),
            'teenager': (100, 120),
            'adult': (90, 140),
            'elderly': (90, 150)
        },
        'blood_pressure_diastolic': {
            'newborn': (30, 60),
            'infant': (50, 70),
            'child': (60, 75),
            'teenager': (60, 80),
            'adult': (60, 90),
            'elderly': (60, 90)
        },
        'temperature': {
            'all': (36.0, 37.5)  # °C
        },
        'oxygen_saturation': {
            'all': (95, 100)     # %
        }
    }
    
    @classmethod
    def validate_cpf(cls, cpf: str) -> bool:
        """Valida CPF brasileiro"""
        # Remover caracteres não numéricos
        cpf_clean = re.sub(r'\D', '', cpf)
        
        # Verificar tamanho
        if len(cpf_clean) != 11:
            return False
        
        # Verificar se todos os dígitos são iguais
        if len(set(cpf_clean)) == 1:
            return False
        
        # Calcular primeiro dígito verificador
        sum_digits = sum(int(cpf_clean[i]) * (10 - i) for i in range(9))
        first_digit = (sum_digits * 10) % 11
        first_digit = 0 if first_digit == 10 else first_digit
        
        if int(cpf_clean[9]) != first_digit:
            return False
        
        # Calcular segundo dígito verificador
        sum_digits = sum(int(cpf_clean[i]) * (11 - i) for i in range(10))
        second_digit = (sum_digits * 10) % 11
        second_digit = 0 if second_digit == 10 else second_digit
        
        return int(cpf_clean[10]) == second_digit
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Valida número de telefone"""
        return bool(cls.PHONE_PATTERN.match(phone))
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Valida endereço de email"""
        return bool(cls.EMAIL_PATTERN.match(email.lower()))
    
    @classmethod
    def validate_date_of_birth(cls, dob: date) -> Tuple[bool, Optional[str]]:
        """Valida data de nascimento"""
        today = date.today()
        
        if dob > today:
            return False, "Data de nascimento não pode ser no futuro"
        
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age > 150:
            return False, "Idade inválida (maior que 150 anos)"
        
        return True, None
    
    @classmethod
    def validate_blood_test_results(
        cls,
        results: Dict[str, float],
        gender: Gender = Gender.OTHER,
        age: Optional[int] = None
    ) -> Dict[str, Any]:
        """Valida resultados de exame de sangue"""
        validation_results = {}
        alerts = []
        
        for param, value in results.items():
            if param not in cls.BLOOD_REFERENCE_RANGES:
                continue
            
            ref_range = cls.BLOOD_REFERENCE_RANGES[param]
            status = 'normal'
            reference = None
            
            # Determinar faixa de referência
            if gender.value in ref_range:
                reference = ref_range[gender.value]
            elif 'all' in ref_range:
                reference = ref_range['all']
            else:
                # Para parâmetros com múltiplas categorias
                for category, range_values in ref_range.items():
                    if category not in ['unit', 'male', 'female']:
                        reference = range_values
                        break
            
            if reference and isinstance(reference, tuple):
                min_val, max_val = reference
                
                if value < min_val:
                    status = 'low'
                    alerts.append({
                        'parameter': param,
                        'value': value,
                        'status': status,
                        'reference': reference,
                        'unit': ref_range.get('unit', '')
                    })
                elif value > max_val:
                    status = 'high'
                    alerts.append({
                        'parameter': param,
                        'value': value,
                        'status': status,
                        'reference': reference,
                        'unit': ref_range.get('unit', '')
                    })
            
            validation_results[param] = {
                'value': value,
                'status': status,
                'reference': reference,
                'unit': ref_range.get('unit', '')
            }
        
        return {
            'valid': True,
            'results': validation_results,
            'alerts': alerts,
            'has_alerts': len(alerts) > 0
        }
    
    @classmethod
    def validate_vital_signs(
        cls,
        vital_signs: Dict[str, float],
        age: int
    ) -> Dict[str, Any]:
        """Valida sinais vitais baseado na idade"""
        # Determinar categoria de idade
        if age < 0.08:  # < 1 mês
            age_category = 'newborn'
        elif age < 1:
            age_category = 'infant'
        elif age < 12:
            age_category = 'child'
        elif age < 18:
            age_category = 'teenager'
        elif age < 65:
            age_category = 'adult'
        else:
            age_category = 'elderly'
        
        validation_results = {}
        alerts = []
        
        for sign, value in vital_signs.items():
            if sign not in cls.VITAL_SIGNS_RANGES:
                continue
            
            ranges = cls.VITAL_SIGNS_RANGES[sign]
            
            if age_category in ranges:
                min_val, max_val = ranges[age_category]
            elif 'all' in ranges:
                min_val, max_val = ranges['all']
            else:
                continue
            
            status = 'normal'
            
            if value < min_val:
                status = 'low'
                alerts.append({
                    'parameter': sign,
                    'value': value,
                    'status': status,
                    'reference': (min_val, max_val)
                })
            elif value > max_val:
                status = 'high'
                alerts.append({
                    'parameter': sign,
                    'value': value,
                    'status': status,
                    'reference': (min_val, max_val)
                })
            
            validation_results[sign] = {
                'value': value,
                'status': status,
                'reference': (min_val, max_val),
                'age_category': age_category
            }
        
        return {
            'valid': True,
            'results': validation_results,
            'alerts': alerts,
            'has_alerts': len(alerts) > 0,
            'age_category': age_category
        }
    
    @classmethod
    def validate_ecg_data(
        cls,
        ecg_data: Dict[str, Any],
        leads: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Valida dados de ECG"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validar frequência cardíaca
        if 'heart_rate' in ecg_data:
            hr = ecg_data['heart_rate']
            if hr < MIN_HEART_RATE:
                validation_results['warnings'].append(
                    f"Frequência cardíaca baixa: {hr} bpm"
                )
            elif hr > MAX_HEART_RATE:
                validation_results['warnings'].append(
                    f"Frequência cardíaca alta: {hr} bpm"
                )
        
        # Validar dados brutos
        if 'raw_data' in ecg_data:
            raw_data = ecg_data['raw_data']
            
            if isinstance(raw_data, list):
                raw_data = np.array(raw_data)
            
            # Verificar dimensões
            expected_samples = ECG_SAMPLE_RATE * ECG_DURATION
            
            if raw_data.ndim == 1:
                # Dados de uma derivação
                if len(raw_data) != expected_samples:
                    validation_results['errors'].append(
                        f"Número incorreto de amostras: {len(raw_data)} "
                        f"(esperado: {expected_samples})"
                    )
            elif raw_data.ndim == 2:
                # Dados de múltiplas derivações
                n_leads, n_samples = raw_data.shape
                
                if n_samples != expected_samples:
                    validation_results['errors'].append(
                        f"Número incorreto de amostras: {n_samples} "
                        f"(esperado: {expected_samples})"
                    )
                
                if leads and n_leads != len(leads):
                    validation_results['errors'].append(
                        f"Número de derivações não corresponde: {n_leads} "
                        f"(esperado: {len(leads)})"
                    )
            
            # Verificar valores
            if np.any(np.isnan(raw_data)):
                validation_results['errors'].append(
                    "Dados contêm valores NaN"
                )
            
            if np.any(np.isinf(raw_data)):
                validation_results['errors'].append(
                    "Dados contêm valores infinitos"
                )
            
            # Verificar amplitude (em mV)
            max_amplitude = np.max(np.abs(raw_data))
            if max_amplitude > 5.0:  # 5 mV é um limite razoável
                validation_results['warnings'].append(
                    f"Amplitude máxima muito alta: {max_amplitude:.2f} mV"
                )
        
        # Validar intervalos
        intervals = ['pr_interval', 'qrs_duration', 'qt_interval']
        normal_ranges = {
            'pr_interval': (120, 200),      # ms
            'qrs_duration': (80, 120),      # ms
            'qt_interval': (350, 450)       # ms
        }
        
        for interval in intervals:
            if interval in ecg_data:
                value = ecg_data[interval]
                min_val, max_val = normal_ranges[interval]
                
                if value < min_val or value > max_val:
                    validation_results['warnings'].append(
                        f"{interval} fora da faixa normal: {value} ms "
                        f"(normal: {min_val}-{max_val} ms)"
                    )
        
        # Definir validade geral
        validation_results['valid'] = len(validation_results['errors']) == 0
        
        return validation_results
    
    @classmethod
    def validate_medication_dosage(
        cls,
        medication: str,
        dosage: float,
        unit: str,
        weight: Optional[float] = None,
        age: Optional[int] = None
    ) -> Dict[str, Any]:
        """Valida dosagem de medicamento"""
        # Esta é uma implementação simplificada
        # Em produção, usar base de dados de medicamentos
        
        validation_result = {
            'valid': True,
            'warnings': [],
            'recommendations': []
        }
        
        # Verificar unidade
        valid_units = ['mg', 'g', 'mcg', 'ml', 'UI', 'mg/kg', 'mcg/kg']
        if unit not in valid_units:
            validation_result['valid'] = False
            validation_result['warnings'].append(
                f"Unidade inválida: {unit}"
            )
        
        # Verificar dosagem baseada em peso (se aplicável)
        if unit.endswith('/kg') and weight:
            total_dose = dosage * weight
            validation_result['recommendations'].append(
                f"Dose total: {total_dose:.2f} {unit.replace('/kg', '')}"
            )
        
        # Adicionar recomendações gerais
        if age and age < 12:
            validation_result['recommendations'].append(
                "Verificar dosagem pediátrica"
            )
        elif age and age > 65:
            validation_result['recommendations'].append(
                "Considerar ajuste de dose para idosos"
            )
        
        return validation_result
    
    @classmethod
    def validate_image_file(
        cls,
        file_path: str,
        exam_type: ExamType
    ) -> Dict[str, Any]:
        """Valida arquivo de imagem médica"""
        import os
        from pathlib import Path
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        # Verificar se arquivo existe
        if not os.path.exists(file_path):
            validation_result['valid'] = False
            validation_result['errors'].append("Arquivo não encontrado")
            return validation_result
        
        # Verificar extensão
        file_ext = Path(file_path).suffix.lower()
        valid_extensions = {
            ExamType.XRAY: ['.dcm', '.jpg', '.jpeg', '.png'],
            ExamType.CT_SCAN: ['.dcm', '.nii', '.nii.gz'],
            ExamType.MRI: ['.dcm', '.nii', '.nii.gz'],
            ExamType.ULTRASOUND: ['.dcm', '.jpg', '.jpeg', '.png']
        }
        
        if exam_type in valid_extensions:
            if file_ext not in valid_extensions[exam_type]:
                validation_result['warnings'].append(
                    f"Extensão {file_ext} não é típica para {exam_type.value}"
                )
        
        # Verificar tamanho
        file_size = os.path.getsize(file_path)
        validation_result['metadata']['size_mb'] = file_size / (1024 * 1024)
        
        if file_size > 100 * 1024 * 1024:  # 100 MB
            validation_result['warnings'].append(
                "Arquivo muito grande (> 100 MB)"
            )
        
        # Para arquivos DICOM
        if file_ext == '.dcm':
            try:
                import pydicom
                ds = pydicom.dcmread(file_path)
                
                # Extrair metadados relevantes
                validation_result['metadata']['modality'] = str(ds.get('Modality', ''))
                validation_result['metadata']['study_date'] = str(ds.get('StudyDate', ''))
                validation_result['metadata']['patient_id'] = str(ds.get('PatientID', ''))
                
                # Verificar modalidade
                expected_modalities = {
                    ExamType.XRAY: ['CR', 'DX'],
                    ExamType.CT_SCAN: ['CT'],
                    ExamType.MRI: ['MR'],
                    ExamType.ULTRASOUND: ['US']
                }
                
                if exam_type in expected_modalities:
                    modality = ds.get('Modality', '')
                    if modality not in expected_modalities[exam_type]:
                        validation_result['warnings'].append(
                            f"Modalidade {modality} não corresponde ao tipo de exame {exam_type.value}"
                        )
                
            except Exception as e:
                validation_result['errors'].append(
                    f"Erro ao ler arquivo DICOM: {str(e)}"
                )
                validation_result['valid'] = False
        
        return validation_result
    
    @classmethod
    def validate_lab_report(
        cls,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida relatório laboratorial completo"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sections': {}
        }
        
        # Campos obrigatórios
        required_fields = ['patient_id', 'exam_date', 'exam_type', 'results']
        
        for field in required_fields:
            if field not in report_data:
                validation_result['errors'].append(
                    f"Campo obrigatório ausente: {field}"
                )
                validation_result['valid'] = False
        
        # Validar data do exame
        if 'exam_date' in report_data:
            try:
                exam_date = datetime.fromisoformat(report_data['exam_date'])
                if exam_date > datetime.now():
                    validation_result['errors'].append(
                        "Data do exame não pode ser no futuro"
                    )
                    validation_result['valid'] = False
            except:
                validation_result['errors'].append(
                    "Formato de data inválido"
                )
                validation_result['valid'] = False
        
        # Validar resultados específicos por tipo
        if 'exam_type' in report_data and 'results' in report_data:
            exam_type = report_data['exam_type']
            results = report_data['results']
            
            if exam_type == 'blood_test':
                # Validar exame de sangue
                gender = Gender(report_data.get('patient_gender', 'other'))
                age = report_data.get('patient_age')
                
                blood_validation = cls.validate_blood_test_results(
                    results, gender, age
                )
                validation_result['sections']['blood_test'] = blood_validation
                
                if blood_validation['has_alerts']:
                    validation_result['warnings'].extend([
                        f"{alert['parameter']}: {alert['status']}"
                        for alert in blood_validation['alerts']
                    ])
        
        return validation_result
    
    @classmethod
    def calculate_bmi(cls, weight: float, height: float) -> Dict[str, Any]:
        """Calcula e classifica IMC"""
        # Altura em metros, peso em kg
        bmi = weight / (height ** 2)
        
        # Classificação OMS
        if bmi < 18.5:
            classification = "Abaixo do peso"
        elif bmi < 25:
            classification = "Peso normal"
        elif bmi < 30:
            classification = "Sobrepeso"
        elif bmi < 35:
            classification = "Obesidade grau I"
        elif bmi < 40:
            classification = "Obesidade grau II"
        else:
            classification = "Obesidade grau III"
        
        return {
            'bmi': round(bmi, 2),
            'classification': classification,
            'weight': weight,
            'height': height
        }
    
    @classmethod
    def validate_patient_data(
        cls,
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida dados completos do paciente"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'fields': {}
        }
        
        # Validar CPF
        if 'cpf' in patient_data:
            if not cls.validate_cpf(patient_data['cpf']):
                validation_result['errors'].append("CPF inválido")
                validation_result['fields']['cpf'] = 'invalid'
            else:
                validation_result['fields']['cpf'] = 'valid'
        
        # Validar email
        if 'email' in patient_data:
            if not cls.validate_email(patient_data['email']):
                validation_result['errors'].append("Email inválido")
                validation_result['fields']['email'] = 'invalid'
            else:
                validation_result['fields']['email'] = 'valid'
        
        # Validar telefone
        if 'phone' in patient_data:
            if not cls.validate_phone(patient_data['phone']):
                validation_result['warnings'].append("Formato de telefone pode estar incorreto")
                validation_result['fields']['phone'] = 'warning'
            else:
                validation_result['fields']['phone'] = 'valid'
        
        # Validar data de nascimento
        if 'date_of_birth' in patient_data:
            try:
                dob = datetime.fromisoformat(patient_data['date_of_birth']).date()
                valid, message = cls.validate_date_of_birth(dob)
                
                if not valid:
                    validation_result['errors'].append(message)
                    validation_result['fields']['date_of_birth'] = 'invalid'
                else:
                    validation_result['fields']['date_of_birth'] = 'valid'
            except:
                validation_result['errors'].append("Formato de data inválido")
                validation_result['fields']['date_of_birth'] = 'invalid'
        
        # Calcular IMC se peso e altura disponíveis
        if 'weight' in patient_data and 'height' in patient_data:
            try:
                bmi_data = cls.calculate_bmi(
                    patient_data['weight'],
                    patient_data['height']
                )
                validation_result['fields']['bmi'] = bmi_data
            except:
                validation_result['warnings'].append("Não foi possível calcular IMC")
        
        validation_result['valid'] = len(validation_result['errors']) == 0
        
        return validation_result

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationResult:
    """Validation result class"""
    
    def __init__(self, is_valid: bool, message: str = None, code: str = None, data: dict = None):
        self.is_valid = is_valid
        self.message = message or ("Validation passed" if is_valid else "Validation failed")
        self.code = code
        self.data = data or {}
        self.errors = []
        self.warnings = []
    
    def add_error(self, error: str, field: str = None):
        """Add validation error"""
        self.errors.append({"message": error, "field": field})
        self.is_valid = False
    
    def add_warning(self, warning: str, field: str = None):
        """Add validation warning"""
        self.warnings.append({"message": warning, "field": field})
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "message": self.message,
            "code": self.code,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings
        }
