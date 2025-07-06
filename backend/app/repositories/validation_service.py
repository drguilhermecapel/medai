"""
Serviço de validação de dados do MedAI
Centraliza validações de dados médicos, arquivos e regras de negócio
"""
import re
import mimetypes
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass

from app.core.constants import (
    ExamType, UserRole, Gender, VALIDATION_RULES, 
    EXAM_VALIDATION_RULES, FILE_EXTENSIONS
)
from app.core.exceptions import ValidationError, InvalidInputError, InvalidFileTypeError
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Resultado de uma validação"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    field_errors: Dict[str, List[str]]
    
    def add_error(self, error: str, field: str = None):
        """Adiciona erro à validação"""
        self.errors.append(error)
        self.is_valid = False
        
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(error)
    
    def add_warning(self, warning: str):
        """Adiciona aviso à validação"""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "field_errors": self.field_errors
        }


class ValidationService:
    """Serviço central de validação"""
    
    def __init__(self):
        self.logger = logger
    
    # === VALIDAÇÕES BÁSICAS ===
    
    def validate_email(self, email: str) -> ValidationResult:
        """
        Valida formato de email
        
        Args:
            email: Email para validar
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(True, [], [], {})
        
        if not email:
            result.add_error("Email é obrigatório", "email")
            return result
        
        # Validar formato
        pattern = VALIDATION_RULES["email"]["pattern"]
        if not re.match(pattern, email):
            result.add_error("Formato de email inválido", "email")
        
        # Validar comprimento
        max_length = VALIDATION_RULES["email"]["max_length"]
        if len(email) > max_length:
            result.add_error(f"Email muito longo (máximo {max_length} caracteres)", "email")
        
        # Verificar domínios suspeitos
        suspicious_domains = ["example.com", "test.com", "fake.com"]
        domain = email.split("@")[-1].lower()
        if domain in suspicious_domains:
            result.add_warning(f"Domínio suspeito: {domain}")
        
        return result
    
    def validate_phone(self, phone: str) -> ValidationResult:
        """
        Valida número de telefone
        
        Args:
            phone: Telefone para validar
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(True, [], [], {})
        
        if not phone:
            return result  # Telefone é opcional em muitos casos
        
        # Limpar formatação
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Validar formato
        pattern = VALIDATION_RULES["phone"]["pattern"]
        if not re.match(pattern, clean_phone):
            result.add_error("Formato de telefone inválido", "phone")
        
        # Validar comprimento
        max_length = VALIDATION_RULES["phone"]["max_length"]
        if len(clean_phone) > max_length:
            result.add_error(f"Telefone muito longo (máximo {max_length} dígitos)", "phone")
        
        return result
    
    def validate_name(self, name: str, field_name: str = "name") -> ValidationResult:
        """
        Valida nome de pessoa
        
        Args:
            name: Nome para validar
            field_name: Nome do campo para erros
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(True, [], [], {})
        
        if not name:
            result.add_error(f"{field_name.title()} é obrigatório", field_name)
            return result
        
        name = name.strip()
        rules = VALIDATION_RULES["name"]
        
        # Validar comprimento
        if len(name) < rules["min_length"]:
            result.add_error(
                f"{field_name.title()} deve ter pelo menos {rules['min_length']} caracteres",
                field_name
            )
        
        if len(name) > rules["max_length"]:
            result.add_error(
                f"{field_name.title()} deve ter no máximo {rules['max_length']} caracteres",
                field_name
            )
        
        # Validar caracteres permitidos
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        allowed_chars.update(rules["allow_special_chars"])
        
        for char in name:
            if char not in allowed_chars:
                result.add_error(f"Caractere não permitido em {field_name}: '{char}'", field_name)
                break
        
        # Verificar padrões suspeitos
        if re.search(r'\d{3,}', name):  # 3 ou mais números seguidos
            result.add_warning(f"{field_name.title()} contém muitos números")
        
        return result
    
    def validate_cpf(self, cpf: str) -> ValidationResult:
        """
        Valida CPF brasileiro
        
        Args:
            cpf: CPF para validar
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(True, [], [], {})
        
        if not cpf:
            return result  # CPF pode ser opcional
        
        # Limpar formatação
        clean_cpf = re.sub(r'[^\d]', '', cpf)
        
        # Verificar comprimento
        if len(clean_cpf) != 11:
            result.add_error("CPF deve ter 11 dígitos", "cpf")
            return result
        
        # Verificar sequências inválidas
        invalid_sequences = [
            "00000000000", "11111111111", "22222222222", "33333333333",
            "44444444444", "55555555555", "66666666666", "77777777777",
            "88888888888", "99999999999"
        ]
        
        if clean_cpf in invalid_sequences:
            result.add_error("CPF inválido", "cpf")
            return result
        
        # Validar dígitos verificadores
        def calculate_digit(cpf_digits: str, weights: List[int]) -> int:
            total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, weights))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        # Primeiro dígito verificador
        first_digit = calculate_digit(clean_cpf[:9], list(range(10, 1, -1)))
        if int(clean_cpf[9]) != first_digit:
            result.add_error("CPF inválido", "cpf")
            return result
        
        # Segundo dígito verificador
        second_digit = calculate_digit(clean_cpf[:10], list(range(11, 1, -1)))
        if int(clean_cpf[10]) != second_digit:
            result.add_error("CPF inválido", "cpf")
            return result
        
        return result
    
    def validate_date(
        self, 
        date_value: Union[str, date, datetime], 
        field_name: str = "date",
        min_date: date = None,
        max_date: date = None
    ) -> ValidationResult:
        """
        Valida data
        
        Args:
            date_value: Data para validar
            field_name: Nome do campo
            min_date: Data mínima permitida
            max_date: Data máxima permitida
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(True, [], [], {})
        
        if not date_value:
            result.add_error(f"{field_name.title()} é obrigatória", field_name)
            return result
        
        # Converter para date se necessário
        if isinstance(date_value, str):
            try:
                # Tentar formatos comuns
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                    try:
                        parsed_date = datetime.strptime(date_value, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    result.add_error(f"Formato de data inválido em {field_name}", field_name)
                    return result
                
                date_value = parsed_date
                
            except ValueError:
                result.add_error(f"Data inválida em {field_name}", field_name)
                return result
        
        elif isinstance(date_value, datetime):
            date_value = date_value.date()
        
        # Validar limites
        if min_date and date_value < min_date:
            result.add_error(
                f"{field_name.title()} não pode ser anterior a {min_date.strftime('%d/%m/%Y')}",
                field_name
            )
        
        if max_date and date_value > max_date:
            result.add_error(
                f"{field_name.title()} não pode ser posterior a {max_date.strftime('%d/%m/%Y')}",
                field_name
            )
        
        return result
    
    def validate_birth_date(self, birth_date: Union[str, date, datetime]) -> ValidationResult:
        """
        Valida data de nascimento
        
        Args:
            birth_date: Data de nascimento
            
        Returns:
            Resultado da validação
        """
        today = date.today()
        min_date = date(1900, 1, 1)  # Idade máxima razoável
        
        result = self.validate_date(birth_date, "birth_date", min_date, today)
        
        # Validações específicas de nascimento
        if result.is_valid and isinstance(birth_date, (date, datetime)):
            if isinstance(birth_date, datetime):
                birth_date = birth_date.date()
            
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 0:
                result.add_error("Data de nascimento não pode ser no futuro", "birth_date")
            elif age > 150:
                result.add_warning("Idade muito avançada - verificar data")
            elif age == 0:
                result.add_warning("Recém-nascido - verificar data")
        
        return result
    
    # === VALIDAÇÕES MÉDICAS ===
    
    def validate_patient_data(self, patient_data: Dict[str, Any]) -> ValidationResult:
        """
        Valida dados de paciente
        
        Args:
            patient_data: Dados do paciente
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(True, [], [], {})
        
        # Campos obrigatórios
        required_fields = ["first_name", "last_name", "birth_date", "gender"]
        for field in required_fields:
            if not patient_data.get(field):
                result.add_error(f"Campo obrigatório: {field}", field)
        
        # Validar campos específicos
        if "email" in patient_data and patient_data["email"]:
            email_result = self.validate_email(patient_data["email"])
            if not email_result.is_valid:
                result.errors.extend(email_result.errors)
                result.field_errors.update(email_result.field_errors)
                result.is_valid = False
        
        if "phone_primary" in patient_data and patient_data["phone_primary"]:
            phone_result = self.validate_phone(patient_data["phone_primary"])
            if not phone_result.is_valid:
                result.errors.extend(phone_result.errors)
                result.field_errors.update(phone_result.field_errors)
                result.is_valid = False
        
        if "cpf" in patient_data and patient_data["cpf"]:
            cpf_result = self.validate_cpf(patient_data["cpf"])
            if not cpf_result.is_valid:
                result.errors.extend(cpf_result.errors)
                result.field_errors.update(cpf_result.field_errors)
                result.is_valid = False
        
        if "birth_date" in patient_data:
            birth_result = self.validate_birth_date(patient_data["birth_date"])
            if not birth_result.is_valid:
                result.errors.extend(birth_result.errors)
                result.field_errors.update(birth_result.field_errors)
                result.is_valid = False
            result.warnings.extend(birth_result.warnings)
        
        # Validar medidas físicas
        if "height" in patient_data and patient_data["height"]:
            height = float(patient_data["height"])
            if height < 0.3 or height > 3.0:
                result.add_error("Altura deve estar entre 30cm e 3m", "height")
        
        if "weight" in patient_data and patient_data["weight"]:
            weight = float(patient_data["weight"])
            if weight < 0.5 or weight > 500:
                result.add_error("Peso deve estar entre 0.5kg e 500kg", "weight")
        
        return result
    
    def validate_exam_data(self, exam_data: Dict[str, Any]) -> ValidationResult:
        """
        Valida dados de exame
        
        Args:
            exam_data: Dados do exame
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(True, [], [], {})
        
        # Campos obrigatórios
        required_fields = ["patient_id", "physician_id", "exam_type", "title"]
        for field in required_fields:
            if not exam_data.get(field):
                result.add_error(f"Campo obrigatório: {field}", field)
        
        # Validar tipo de exame
        exam_type = exam_data.get("exam_type")
        if exam_type:
            try:
                ExamType(exam_type)
            except ValueError:
                result.add_error(f"Tipo de exame inválido: {exam_type}", "exam_type")
        
        # Validar IDs como UUID
        uuid_fields = ["patient_id", "physician_id", "technician_id"]
        for field in uuid_fields:
            if field in exam_data and exam_data[field]:
                try:
                    uuid.UUID(str(exam_data[field]))
                except ValueError:
                    result.add_error(f"ID inválido em {field}", field)
        
        # Validar datas
        if "scheduled_date" in exam_data and exam_data["scheduled_date"]:
            # Data agendada não pode ser no passado
            min_date = datetime.now().date()
            date_result = self.validate_date(
                exam_data["scheduled_date"], 
                "scheduled_date", 
                min_date=min_date
            )
            if not date_result.is_valid:
                result.errors.extend(date_result.errors)
                result.field_errors.update(date_result.field_errors)
                result.is_valid = False
        
        # Validações específicas por tipo de exame
        if exam_type and exam_type in EXAM_VALIDATION_RULES:
            rules = EXAM_VALIDATION_RULES[exam_type]
            
            # Verificar campos obrigatórios específicos
            for required_field in rules.get("required_fields", []):
                if not exam_data.get(required_field):
                    result.add_error(
                        f"Campo obrigatório para {exam_type}: {required_field}",
                        required_field
                    )
        
        return result
    
    def validate_diagnostic_data(self, diagnostic_data: Dict[str, Any]) -> ValidationResult:
        """
        Valida dados de diagnóstico
        
        Args:
            diagnostic_data: Dados do diagnóstico
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(True, [], [], {})
        
        # Campos obrigatórios
        required_fields = ["exam_id", "patient_id"]
        for field in required_fields:
            if not diagnostic_data.get(field):
                result.add_error(f"Campo obrigatório: {field}", field)
        
        # Validar confiança da IA
        if "ai_confidence" in diagnostic_data:
            confidence = diagnostic_data["ai_confidence"]
            if confidence is not None:
                try:
                    confidence_float = float(confidence)
                    if not 0.0 <= confidence_float <= 1.0:
                        result.add_error("Confiança da IA deve estar entre 0.0 e 1.0", "ai_confidence")
                except ValueError:
                    result.add_error("Confiança da IA deve ser um número", "ai_confidence")
        
        # Validar códigos médicos
        if "icd10_codes" in diagnostic_data:
            icd10_codes = diagnostic_data["icd10_codes"]
            if isinstance(icd10_codes, list):
                for code in icd10_codes:
                    if not self._validate_icd10_code(code):
                        result.add_error(f"Código CID-10 inválido: {code}", "icd10_codes")
        
        return result
    
    def _validate_icd10_code(self, code: str) -> bool:
        """
        Valida formato de código CID-10
        
        Args:
            code: Código CID-10
            
        Returns:
            True se válido
        """
        # Formato básico: letra + 2-3 dígitos + opcional ponto + 1-2 dígitos
        pattern = r'^[A-Z]\d{2,3}(\.\d{1,2})?$'
        return bool(re.match(pattern, code.upper()))
    
    # === VALIDAÇÕES DE ARQUIVO ===
    
    def validate_file(
        self, 
        file_path: str, 
        allowed_types: List[str] = None,
        max_size_mb: float = None
    ) -> ValidationResult:
        """
        Valida arquivo
        
        Args:
            file_path: Caminho do arquivo
            allowed_types: Tipos permitidos
            max_size_mb: Tamanho máximo em MB
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(True, [], [], {})
        
        file_path_obj = Path(file_path)
        
        # Verificar se arquivo existe
        if not file_path_obj.exists():
            result.add_error("Arquivo não encontrado", "file")
            return result
        
        # Verificar extensão
        extension = file_path_obj.suffix.lower().lstrip('.')
        if allowed_types and extension not in allowed_types:
            result.add_error(
                f"Tipo de arquivo não permitido: {extension}. Permitidos: {', '.join(allowed_types)}",
                "file"
            )
        
        # Verificar tamanho
        file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
        if max_size_mb and file_size_mb > max_size_mb:
            result.add_error(
                f"Arquivo muito grande: {file_size_mb:.1f}MB (máximo: {max_size_mb}MB)",
                "file"
            )
        
        # Verificar MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path_obj))
        if mime_type:
            # Verificar se MIME type corresponde à extensão
            expected_extensions = mimetypes.guess_all_extensions(mime_type)
            if file_path_obj.suffix.lower() not in expected_extensions:
                result.add_warning(f"Extensão pode não corresponder ao tipo de arquivo: {mime_type}")
        
        return result
    
    def validate_medical_image(self, file_path: str, exam_type: str = None) -> ValidationResult:
        """
        Valida imagem médica
        
        Args:
            file_path: Caminho da imagem
            exam_type: Tipo de exame (opcional)
            
        Returns:
            Resultado da validação
        """
        # Tipos permitidos para imagens médicas
        allowed_types = FILE_EXTENSIONS["image"] + FILE_EXTENSIONS["medical"]
        
        # Tamanho máximo baseado no tipo de exame
        max_size_mb = 50  # Padrão
        if exam_type:
            exam_rules = EXAM_VALIDATION_RULES.get(exam_type, {})
            max_size_mb = exam_rules.get("max_file_size", 50 * 1024 * 1024) / (1024 * 1024)
        
        result = self.validate_file(file_path, allowed_types, max_size_mb)
        
        # Validações específicas para imagens médicas
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower().lstrip('.')
        
        if extension in ["dcm", "dicom"]:
            # Validações específicas para DICOM
            result.warnings.extend(self._validate_dicom_file(file_path))
        
        return result
    
    def _validate_dicom_file(self, file_path: str) -> List[str]:
        """
        Valida arquivo DICOM
        
        Args:
            file_path: Caminho do arquivo DICOM
            
        Returns:
            Lista de avisos
        """
        warnings = []
        
        try:
            # Aqui seria feita validação real de DICOM
            # Por enquanto, apenas verificações básicas
            
            with open(file_path, 'rb') as f:
                # Verificar header DICOM
                f.seek(128)  # Pular preâmbulo
                dicm = f.read(4)
                if dicm != b'DICM':
                    warnings.append("Arquivo pode não ser DICOM válido")
            
        except Exception as e:
            warnings.append(f"Erro ao validar DICOM: {str(e)}")
        
        return warnings
    
    # === VALIDAÇÕES COMPOSTAS ===
    
    def validate_complete_patient(self, patient_data: Dict[str, Any]) -> ValidationResult:
        """
        Validação completa de paciente incluindo relacionamentos
        
        Args:
            patient_data: Dados completos do paciente
            
        Returns:
            Resultado da validação completa
        """
        result = self.validate_patient_data(patient_data)
        
        # Validações adicionais de consistência
        if result.is_valid:
            # Verificar consistência entre idade e dados médicos
            if "birth_date" in patient_data and "current_medications" in patient_data:
                birth_date = patient_data["birth_date"]
                if isinstance(birth_date, str):
                    birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
                
                age = (date.today() - birth_date).days // 365
                medications = patient_data["current_medications"]
                
                # Avisos baseados na idade
                if age < 18 and medications:
                    result.add_warning("Paciente menor de idade com medicações - verificar dosagens")
                elif age > 65 and len(medications) > 5:
                    result.add_warning("Paciente idoso com muitas medicações - verificar interações")
        
        return result
    
    def validate_batch_data(
        self, 
        data_list: List[Dict[str, Any]], 
        validation_type: str
    ) -> Dict[str, Any]:
        """
        Valida lote de dados
        
        Args:
            data_list: Lista de dados para validar
            validation_type: Tipo de validação (patient, exam, diagnostic)
            
        Returns:
            Resultado da validação em lote
        """
        validation_methods = {
            "patient": self.validate_patient_data,
            "exam": self.validate_exam_data,
            "diagnostic": self.validate_diagnostic_data
        }
        
        if validation_type not in validation_methods:
            raise ValueError(f"Tipo de validação não suportado: {validation_type}")
        
        validation_method = validation_methods[validation_type]
        
        results = {
            "total": len(data_list),
            "valid": 0,
            "invalid": 0,
            "details": [],
            "summary_errors": [],
            "summary_warnings": []
        }
        
        for i, data_item in enumerate(data_list):
            result = validation_method(data_item)
            
            item_result = {
                "index": i,
                "is_valid": result.is_valid,
                "errors": result.errors,
                "warnings": result.warnings,
                "field_errors": result.field_errors
            }
            
            results["details"].append(item_result)
            
            if result.is_valid:
                results["valid"] += 1
            else:
                results["invalid"] += 1
                results["summary_errors"].extend(result.errors)
            
            results["summary_warnings"].extend(result.warnings)
        
        # Estatísticas
        results["success_rate"] = results["valid"] / results["total"] if results["total"] > 0 else 0
        results["unique_errors"] = list(set(results["summary_errors"]))
        results["unique_warnings"] = list(set(results["summary_warnings"]))
        
        return results