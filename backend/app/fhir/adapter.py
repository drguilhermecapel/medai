"""
FHIR Adapter for MedAI
Converts between internal data formats and FHIR R4 resources
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.fhir.resources.patient import (
    FHIRPatient, FHIRName, FHIRIdentifier, FHIRTelecom, 
    FHIRAddress, FHIREncounter, FHIRObservation,
    AdministrativeGender, IdentifierUse, NameUse
)

logger = logging.getLogger(__name__)


class FHIRAdapter:
    """Adapter for converting between internal MedAI format and FHIR R4"""
    
    def __init__(self):
        """Initialize FHIR adapter with mapping rules"""
        self.patient_mapping_rules = {
            'cpf': 'identifier[0].value',
            'nome_completo': 'name[0].given[0] + " " + name[0].family',
            'data_nascimento': 'birthDate',
            'sexo': 'gender',
            'telefone': 'telecom[0].value',
            'email': 'telecom[1].value',
            'endereco': 'address[0]'
        }
        
        # Brazilian-specific systems
        self.brazilian_systems = {
            'cpf': 'http://www.saude.gov.br/fhir/r4/NamingSystem/cpf',
            'cns': 'http://www.saude.gov.br/fhir/r4/NamingSystem/cns',
            'rg': 'http://www.saude.gov.br/fhir/r4/NamingSystem/rg'
        }
    
    def to_fhir_patient(self, internal_patient: Dict[str, Any]) -> FHIRPatient:
        """
        Convert internal patient format to FHIR Patient resource
        
        Args:
            internal_patient: Internal patient data
            
        Returns:
            FHIRPatient resource
        """
        try:
            # Build identifiers
            identifiers = []
            
            # Add medical record number as primary identifier
            if 'medical_record_number' in internal_patient:
                identifiers.append(FHIRIdentifier(
                    use=IdentifierUse.USUAL,
                    system="http://hospital.medai.com/patients",
                    value=str(internal_patient['medical_record_number'])
                ))
            
            # Add CPF if available
            if 'cpf' in internal_patient and internal_patient['cpf']:
                identifiers.append(FHIRIdentifier(
                    use=IdentifierUse.OFFICIAL,
                    system=self.brazilian_systems['cpf'],
                    value=self._format_cpf(internal_patient['cpf'])
                ))
            
            # Add CNS if available
            if 'cns' in internal_patient and internal_patient['cns']:
                identifiers.append(FHIRIdentifier(
                    use=IdentifierUse.OFFICIAL,
                    system=self.brazilian_systems['cns'],
                    value=str(internal_patient['cns'])
                ))
            
            # Build names
            names = []
            if 'nome' in internal_patient or 'sobrenome' in internal_patient:
                given_names = []
                family_name = ""
                
                if 'nome' in internal_patient:
                    # Split nome into given names
                    nome_parts = str(internal_patient['nome']).split()
                    given_names.extend(nome_parts)
                
                if 'sobrenome' in internal_patient:
                    family_name = str(internal_patient['sobrenome'])
                elif 'nome_completo' in internal_patient:
                    # Extract family name from full name
                    full_name_parts = str(internal_patient['nome_completo']).split()
                    if len(full_name_parts) > 1:
                        family_name = full_name_parts[-1]
                        given_names = full_name_parts[:-1]
                    else:
                        given_names = full_name_parts
                
                names.append(FHIRName(
                    use=NameUse.USUAL,
                    family=family_name,
                    given=given_names if given_names else None
                ))
            
            # Build telecom
            telecom = []
            if 'telefone' in internal_patient and internal_patient['telefone']:
                telecom.append(FHIRTelecom(
                    system="phone",
                    value=self._format_phone(internal_patient['telefone']),
                    use="mobile"
                ))
            
            if 'email' in internal_patient and internal_patient['email']:
                telecom.append(FHIRTelecom(
                    system="email",
                    value=str(internal_patient['email']),
                    use="home"
                ))
            
            # Map gender
            gender = self._map_gender(internal_patient.get('sexo'))
            
            # Format birth date
            birth_date = None
            if 'data_nascimento' in internal_patient and internal_patient['data_nascimento']:
                birth_date = self._format_date(internal_patient['data_nascimento'])
            
            # Build address
            addresses = []
            if any(key in internal_patient for key in ['endereco', 'cidade', 'estado', 'cep']):
                address_lines = []
                if 'endereco' in internal_patient and internal_patient['endereco']:
                    address_lines.append(str(internal_patient['endereco']))
                
                addresses.append(FHIRAddress(
                    use="home",
                    type="physical",
                    line=address_lines if address_lines else None,
                    city=internal_patient.get('cidade'),
                    state=internal_patient.get('estado'),
                    postalCode=self._format_cep(internal_patient.get('cep')),
                    country="BR"
                ))
            
            # Create FHIR Patient
            fhir_patient = FHIRPatient(
                id=str(internal_patient.get('id', '')),
                identifier=identifiers if identifiers else None,
                active=internal_patient.get('ativo', True),
                name=names if names else None,
                telecom=telecom if telecom else None,
                gender=gender,
                birthDate=birth_date,
                address=addresses if addresses else None
            )
            
            logger.info("Converted internal patient to FHIR", extra={
                "patient_id": internal_patient.get('id'),
                "identifiers_count": len(identifiers)
            })
            
            return fhir_patient
            
        except Exception as e:
            logger.error(f"Failed to convert patient to FHIR: {e}", extra={
                "patient_id": internal_patient.get('id'),
                "error": str(e)
            })
            raise Exception(f"FHIR conversion failed: {e}")
    
    def from_fhir_patient(self, fhir_patient: FHIRPatient) -> Dict[str, Any]:
        """
        Convert FHIR Patient resource to internal format
        
        Args:
            fhir_patient: FHIR Patient resource
            
        Returns:
            Internal patient data dictionary
        """
        try:
            internal_patient = {}
            
            # Extract ID
            if fhir_patient.id:
                internal_patient['id'] = fhir_patient.id
            
            # Extract identifiers
            if fhir_patient.identifier:
                for identifier in fhir_patient.identifier:
                    if identifier.system == self.brazilian_systems['cpf']:
                        internal_patient['cpf'] = self._clean_cpf(identifier.value)
                    elif identifier.system == self.brazilian_systems['cns']:
                        internal_patient['cns'] = identifier.value
                    elif identifier.system == "http://hospital.medai.com/patients":
                        internal_patient['medical_record_number'] = identifier.value
            
            # Extract names
            if fhir_patient.name:
                primary_name = fhir_patient.name[0]
                if primary_name.given:
                    internal_patient['nome'] = ' '.join(primary_name.given)
                if primary_name.family:
                    internal_patient['sobrenome'] = primary_name.family
                
                # Build full name
                nome_parts = []
                if primary_name.given:
                    nome_parts.extend(primary_name.given)
                if primary_name.family:
                    nome_parts.append(primary_name.family)
                internal_patient['nome_completo'] = ' '.join(nome_parts)
            
            # Extract telecom
            if fhir_patient.telecom:
                for telecom in fhir_patient.telecom:
                    if telecom.system == "phone":
                        internal_patient['telefone'] = self._clean_phone(telecom.value)
                    elif telecom.system == "email":
                        internal_patient['email'] = telecom.value
            
            # Extract gender
            if fhir_patient.gender:
                internal_patient['sexo'] = self._map_gender_from_fhir(fhir_patient.gender)
            
            # Extract birth date
            if fhir_patient.birthDate:
                internal_patient['data_nascimento'] = fhir_patient.birthDate
            
            # Extract address
            if fhir_patient.address:
                primary_address = fhir_patient.address[0]
                if primary_address.line:
                    internal_patient['endereco'] = ', '.join(primary_address.line)
                if primary_address.city:
                    internal_patient['cidade'] = primary_address.city
                if primary_address.state:
                    internal_patient['estado'] = primary_address.state
                if primary_address.postalCode:
                    internal_patient['cep'] = self._clean_cep(primary_address.postalCode)
            
            # Extract active status
            if fhir_patient.active is not None:
                internal_patient['ativo'] = fhir_patient.active
            
            logger.info("Converted FHIR patient to internal format", extra={
                "fhir_patient_id": fhir_patient.id,
                "fields_extracted": len(internal_patient)
            })
            
            return internal_patient
            
        except Exception as e:
            logger.error(f"Failed to convert FHIR patient to internal format: {e}")
            raise Exception(f"FHIR to internal conversion failed: {e}")
    
    # Helper methods for data formatting and mapping
    
    def _format_cpf(self, cpf: str) -> str:
        """Format CPF with standard formatting"""
        if not cpf:
            return ""
        
        # Remove non-digits
        digits = ''.join(filter(str.isdigit, str(cpf)))
        
        # Format as XXX.XXX.XXX-XX
        if len(digits) == 11:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"
        
        return digits
    
    def _clean_cpf(self, cpf: str) -> str:
        """Remove formatting from CPF"""
        if not cpf:
            return ""
        return ''.join(filter(str.isdigit, str(cpf)))
    
    def _format_phone(self, phone: str) -> str:
        """Format Brazilian phone number"""
        if not phone:
            return ""
        
        digits = ''.join(filter(str.isdigit, str(phone)))
        
        # Format as (XX) XXXXX-XXXX or (XX) XXXX-XXXX
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        elif len(digits) == 10:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        
        return digits
    
    def _clean_phone(self, phone: str) -> str:
        """Remove formatting from phone number"""
        if not phone:
            return ""
        return ''.join(filter(str.isdigit, str(phone)))
    
    def _format_cep(self, cep: str) -> str:
        """Format Brazilian postal code"""
        if not cep:
            return ""
        
        digits = ''.join(filter(str.isdigit, str(cep)))
        
        # Format as XXXXX-XXX
        if len(digits) == 8:
            return f"{digits[:5]}-{digits[5:]}"
        
        return digits
    
    def _clean_cep(self, cep: str) -> str:
        """Remove formatting from CEP"""
        if not cep:
            return ""
        return ''.join(filter(str.isdigit, str(cep)))
    
    def _map_gender(self, internal_gender: str) -> Optional[AdministrativeGender]:
        """Map internal gender to FHIR gender"""
        if not internal_gender:
            return None
        
        gender_map = {
            'M': AdministrativeGender.MALE,
            'masculino': AdministrativeGender.MALE,
            'male': AdministrativeGender.MALE,
            'F': AdministrativeGender.FEMALE,
            'feminino': AdministrativeGender.FEMALE,
            'female': AdministrativeGender.FEMALE,
            'outro': AdministrativeGender.OTHER,
            'other': AdministrativeGender.OTHER,
            'desconhecido': AdministrativeGender.UNKNOWN,
            'unknown': AdministrativeGender.UNKNOWN
        }
        
        return gender_map.get(str(internal_gender).lower(), AdministrativeGender.UNKNOWN)
    
    def _map_gender_from_fhir(self, fhir_gender: AdministrativeGender) -> str:
        """Map FHIR gender to internal format"""
        gender_map = {
            AdministrativeGender.MALE: 'M',
            AdministrativeGender.FEMALE: 'F',
            AdministrativeGender.OTHER: 'outro',
            AdministrativeGender.UNKNOWN: 'desconhecido'
        }
        
        return gender_map.get(fhir_gender, 'desconhecido')
    
    def _format_date(self, date_value) -> Optional[str]:
        """Format date to FHIR date format (YYYY-MM-DD)"""
        if not date_value:
            return None
        
        try:
            if isinstance(date_value, str):
                # Try to parse various date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        parsed_date = datetime.strptime(date_value, fmt)
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
                
                return date_value  # Return as-is if can't parse
            
            elif hasattr(date_value, 'strftime'):
                # datetime or date object
                return date_value.strftime('%Y-%m-%d')
            
            else:
                return str(date_value)
                
        except Exception as e:
            logger.warning(f"Failed to format date: {e}")
            return None
    
    def validate_fhir_patient(self, fhir_patient: FHIRPatient) -> List[str]:
        """
        Validate FHIR Patient resource
        
        Args:
            fhir_patient: FHIR Patient to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Resource type validation
        if fhir_patient.resourceType != "Patient":
            errors.append("Invalid resourceType: must be 'Patient'")
        
        # Required elements validation
        if not fhir_patient.identifier and not fhir_patient.name:
            errors.append("Patient must have either identifier or name")
        
        # Identifier validation
        if fhir_patient.identifier:
            for i, identifier in enumerate(fhir_patient.identifier):
                if not identifier.value:
                    errors.append(f"Identifier[{i}] must have a value")
        
        # Name validation
        if fhir_patient.name:
            for i, name in enumerate(fhir_patient.name):
                if not name.family and not name.given:
                    errors.append(f"Name[{i}] must have either family or given name")
        
        # Gender validation
        if fhir_patient.gender and fhir_patient.gender not in [g.value for g in AdministrativeGender]:
            errors.append(f"Invalid gender: {fhir_patient.gender}")
        
        # Birth date format validation
        if fhir_patient.birthDate:
            try:
                datetime.strptime(fhir_patient.birthDate, '%Y-%m-%d')
            except ValueError:
                errors.append("birthDate must be in YYYY-MM-DD format")
        
        return errors


# Global adapter instance
fhir_adapter = FHIRAdapter()