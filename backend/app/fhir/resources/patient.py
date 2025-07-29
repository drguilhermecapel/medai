"""
FHIR R4 Patient Resource for MedAI
Implements FHIR Patient resource structure
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class IdentifierUse(str, Enum):
    """FHIR Identifier use codes"""
    USUAL = "usual"
    OFFICIAL = "official"
    TEMP = "temp"
    SECONDARY = "secondary"
    OLD = "old"


class NameUse(str, Enum):
    """FHIR Name use codes"""
    USUAL = "usual"
    OFFICIAL = "official"
    TEMP = "temp"
    NICKNAME = "nickname"
    ANONYMOUS = "anonymous"
    OLD = "old"
    MAIDEN = "maiden"


class AdministrativeGender(str, Enum):
    """FHIR AdministrativeGender codes"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class FHIRIdentifier(BaseModel):
    """FHIR Identifier datatype"""
    use: Optional[IdentifierUse] = None
    type: Optional[dict] = None
    system: Optional[str] = None
    value: str
    period: Optional[dict] = None
    assigner: Optional[dict] = None
    
    class Config:
        use_enum_values = True


class FHIRName(BaseModel):
    """FHIR HumanName datatype"""
    use: Optional[NameUse] = NameUse.USUAL
    text: Optional[str] = None
    family: Optional[str] = None
    given: Optional[List[str]] = None
    prefix: Optional[List[str]] = None
    suffix: Optional[List[str]] = None
    period: Optional[dict] = None
    
    class Config:
        use_enum_values = True


class FHIRTelecom(BaseModel):
    """FHIR ContactPoint datatype"""
    system: Optional[str] = None  # phone | fax | email | pager | url | sms | other
    value: Optional[str] = None
    use: Optional[str] = None  # home | work | temp | old | mobile
    rank: Optional[int] = None
    period: Optional[dict] = None


class FHIRAddress(BaseModel):
    """FHIR Address datatype"""
    use: Optional[str] = None  # home | work | temp | old | billing
    type: Optional[str] = None  # postal | physical | both
    text: Optional[str] = None
    line: Optional[List[str]] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None
    period: Optional[dict] = None


class FHIRContact(BaseModel):
    """FHIR Patient Contact component"""
    relationship: Optional[List[dict]] = None
    name: Optional[FHIRName] = None
    telecom: Optional[List[FHIRTelecom]] = None
    address: Optional[FHIRAddress] = None
    gender: Optional[AdministrativeGender] = None
    organization: Optional[dict] = None
    period: Optional[dict] = None


class FHIRCommunication(BaseModel):
    """FHIR Patient Communication component"""
    language: dict  # CodeableConcept
    preferred: Optional[bool] = None


class FHIRLink(BaseModel):
    """FHIR Patient Link component"""
    other: dict  # Reference
    type: str  # replaced-by | replaces | refer | seealso


class FHIRPatient(BaseModel):
    """
    FHIR R4 Patient Resource
    
    A person who is the subject of health-related services
    """
    resourceType: Literal["Patient"] = "Patient"
    id: Optional[str] = None
    meta: Optional[dict] = None
    implicitRules: Optional[str] = None
    language: Optional[str] = None
    text: Optional[dict] = None
    contained: Optional[List[dict]] = None
    extension: Optional[List[dict]] = None
    modifierExtension: Optional[List[dict]] = None
    
    # Patient-specific elements
    identifier: Optional[List[FHIRIdentifier]] = None
    active: Optional[bool] = True
    name: Optional[List[FHIRName]] = None
    telecom: Optional[List[FHIRTelecom]] = None
    gender: Optional[AdministrativeGender] = None
    birthDate: Optional[str] = None  # YYYY-MM-DD format
    deceased: Optional[bool] = None  # boolean or dateTime
    address: Optional[List[FHIRAddress]] = None
    maritalStatus: Optional[dict] = None  # CodeableConcept
    multipleBirth: Optional[bool] = None  # boolean or integer
    photo: Optional[List[dict]] = None  # Attachment
    contact: Optional[List[FHIRContact]] = None
    communication: Optional[List[FHIRCommunication]] = None
    generalPractitioner: Optional[List[dict]] = None  # Reference
    managingOrganization: Optional[dict] = None  # Reference
    link: Optional[List[FHIRLink]] = None
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "resourceType": "Patient",
                "id": "example-patient-1",
                "identifier": [
                    {
                        "use": "usual",
                        "system": "http://hospital.example.org/patients",
                        "value": "12345"
                    },
                    {
                        "use": "official",
                        "system": "http://www.saude.gov.br/fhir/r4/NamingSystem/cpf",
                        "value": "123.456.789-00"
                    }
                ],
                "active": True,
                "name": [
                    {
                        "use": "usual",
                        "family": "Silva",
                        "given": ["João", "Carlos"]
                    }
                ],
                "telecom": [
                    {
                        "system": "phone",
                        "value": "(11) 99999-9999",
                        "use": "mobile"
                    },
                    {
                        "system": "email",
                        "value": "joao.silva@example.com",
                        "use": "home"
                    }
                ],
                "gender": "male",
                "birthDate": "1990-01-15",
                "address": [
                    {
                        "use": "home",
                        "type": "physical",
                        "line": ["Rua das Flores, 123"],
                        "city": "São Paulo",
                        "state": "SP",
                        "postalCode": "01234-567",
                        "country": "BR"
                    }
                ]
            }
        }


class FHIREncounter(BaseModel):
    """
    FHIR R4 Encounter Resource
    
    An interaction between a patient and healthcare provider(s)
    """
    resourceType: Literal["Encounter"] = "Encounter"
    id: Optional[str] = None
    meta: Optional[dict] = None
    text: Optional[dict] = None
    
    # Encounter-specific elements
    identifier: Optional[List[FHIRIdentifier]] = None
    status: str  # planned | arrived | triaged | in-progress | onleave | finished | cancelled
    statusHistory: Optional[List[dict]] = None
    class_: Optional[dict] = Field(None, alias="class")  # Coding
    classHistory: Optional[List[dict]] = None
    type: Optional[List[dict]] = None  # CodeableConcept
    serviceType: Optional[dict] = None  # CodeableConcept
    priority: Optional[dict] = None  # CodeableConcept
    subject: Optional[dict] = None  # Reference to Patient
    episodeOfCare: Optional[List[dict]] = None  # Reference
    basedOn: Optional[List[dict]] = None  # Reference
    participant: Optional[List[dict]] = None
    appointment: Optional[List[dict]] = None  # Reference
    period: Optional[dict] = None  # Period
    length: Optional[dict] = None  # Duration
    reasonCode: Optional[List[dict]] = None  # CodeableConcept
    reasonReference: Optional[List[dict]] = None  # Reference
    diagnosis: Optional[List[dict]] = None
    account: Optional[List[dict]] = None  # Reference
    hospitalization: Optional[dict] = None
    location: Optional[List[dict]] = None
    serviceProvider: Optional[dict] = None  # Reference
    partOf: Optional[dict] = None  # Reference
    
    class Config:
        use_enum_values = True
        validate_by_name = True


class FHIRObservation(BaseModel):
    """
    FHIR R4 Observation Resource
    
    Measurements and simple assertions made about a patient
    """
    resourceType: Literal["Observation"] = "Observation"
    id: Optional[str] = None
    meta: Optional[dict] = None
    text: Optional[dict] = None
    
    # Observation-specific elements
    identifier: Optional[List[FHIRIdentifier]] = None
    basedOn: Optional[List[dict]] = None  # Reference
    partOf: Optional[List[dict]] = None  # Reference
    status: str  # registered | preliminary | final | amended | corrected | cancelled | entered-in-error | unknown
    category: Optional[List[dict]] = None  # CodeableConcept
    code: dict  # CodeableConcept - what was observed
    subject: Optional[dict] = None  # Reference to Patient
    focus: Optional[List[dict]] = None  # Reference
    encounter: Optional[dict] = None  # Reference
    effective: Optional[dict] = None  # dateTime | Period | Timing | instant
    issued: Optional[str] = None  # instant
    performer: Optional[List[dict]] = None  # Reference
    value: Optional[dict] = None  # Quantity | CodeableConcept | string | boolean | integer | Range | Ratio | SampledData | time | dateTime | Period
    dataAbsentReason: Optional[dict] = None  # CodeableConcept
    interpretation: Optional[List[dict]] = None  # CodeableConcept
    note: Optional[List[dict]] = None  # Annotation
    bodySite: Optional[dict] = None  # CodeableConcept
    method: Optional[dict] = None  # CodeableConcept
    specimen: Optional[dict] = None  # Reference
    device: Optional[dict] = None  # Reference
    referenceRange: Optional[List[dict]] = None
    hasMember: Optional[List[dict]] = None  # Reference
    derivedFrom: Optional[List[dict]] = None  # Reference
    component: Optional[List[dict]] = None
    
    class Config:
        use_enum_values = True