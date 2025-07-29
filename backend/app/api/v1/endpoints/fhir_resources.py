"""
FHIR R4 API endpoints for MedAI
Implements FHIR-compliant REST API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
import logging

from backend.app.fhir.resources.patient import FHIRPatient, FHIREncounter, FHIRObservation
from backend.app.fhir.adapter import fhir_adapter
from backend.app.core.telemetry.tracing import telemetry

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/Patient", response_model=FHIRPatient, status_code=status.HTTP_201_CREATED)
async def create_patient(patient_data: FHIRPatient):
    """
    Create a new FHIR Patient resource
    
    Args:
        patient_data: FHIR Patient resource data
        
    Returns:
        Created FHIR Patient resource
    """
    with telemetry.create_span("fhir.patient.create") as span:
        try:
            # Validate FHIR Patient
            validation_errors = fhir_adapter.validate_fhir_patient(patient_data)
            if validation_errors:
                telemetry.record_fhir_operation("Patient", "create", False)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": "FHIR_VALIDATION_ERROR",
                        "message": "FHIR Patient validation failed",
                        "details": {"validation_errors": validation_errors}
                    }
                )
            
            # Convert to internal format for storage
            internal_patient = fhir_adapter.from_fhir_patient(patient_data)
            
            span.set_attributes({
                "fhir.resource_type": "Patient",
                "fhir.operation": "create",
                "patient.has_identifiers": len(patient_data.identifier or []) > 0,
                "patient.has_name": len(patient_data.name or []) > 0
            })
            
            # In a real implementation, save to database here
            # For now, just return the validated patient with an ID
            if not patient_data.id:
                import uuid
                patient_data.id = str(uuid.uuid4())
            
            telemetry.record_fhir_operation("Patient", "create", True)
            logger.info("FHIR Patient created", extra={
                "patient_id": patient_data.id,
                "identifier_count": len(patient_data.identifier or [])
            })
            
            return patient_data
            
        except HTTPException:
            raise
        except Exception as e:
            telemetry.record_fhir_operation("Patient", "create", False)
            logger.error(f"Failed to create FHIR Patient: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "FHIR_CREATION_ERROR",
                    "message": "Failed to create FHIR Patient resource",
                    "details": {}
                }
            )


@router.get("/Patient/{patient_id}", response_model=FHIRPatient)
async def get_patient(patient_id: str):
    """
    Get FHIR Patient resource by ID
    
    Args:
        patient_id: Patient resource ID
        
    Returns:
        FHIR Patient resource
    """
    with telemetry.create_span("fhir.patient.read") as span:
        try:
            span.set_attributes({
                "fhir.resource_type": "Patient",
                "fhir.operation": "read",
                "patient.id": patient_id
            })
            
            # In a real implementation, fetch from database here
            # For demo purposes, return a sample patient
            if patient_id == "example":
                sample_patient = FHIRPatient(
                    id=patient_id,
                    resourceType="Patient",
                    identifier=[{
                        "use": "usual",
                        "system": "http://hospital.medai.com/patients",
                        "value": "12345"
                    }],
                    name=[{
                        "use": "usual",
                        "family": "Silva",
                        "given": ["João"]
                    }],
                    gender="male",
                    active=True
                )
                
                telemetry.record_fhir_operation("Patient", "read", True)
                return sample_patient
            
            telemetry.record_fhir_operation("Patient", "read", False)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "PATIENT_NOT_FOUND",
                    "message": f"Patient with ID {patient_id} not found",
                    "details": {}
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            telemetry.record_fhir_operation("Patient", "read", False)
            logger.error(f"Failed to get FHIR Patient: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "FHIR_READ_ERROR",
                    "message": "Failed to retrieve FHIR Patient resource",
                    "details": {}
                }
            )


@router.get("/Patient", response_model=List[FHIRPatient])
async def search_patients(
    family: Optional[str] = None,
    given: Optional[str] = None,
    identifier: Optional[str] = None,
    _count: Optional[int] = 20
):
    """
    Search FHIR Patient resources
    
    Args:
        family: Family name search parameter
        given: Given name search parameter
        identifier: Identifier search parameter
        _count: Maximum number of results to return
        
    Returns:
        List of matching FHIR Patient resources
    """
    with telemetry.create_span("fhir.patient.search") as span:
        try:
            span.set_attributes({
                "fhir.resource_type": "Patient",
                "fhir.operation": "search",
                "search.has_family": family is not None,
                "search.has_given": given is not None,
                "search.has_identifier": identifier is not None,
                "search.count": _count
            })
            
            # In a real implementation, search database here
            # For demo purposes, return empty list or sample data
            results = []
            
            # If searching for a specific test case, return sample data
            if family == "Silva" or given == "João":
                results = [FHIRPatient(
                    id="example-1",
                    resourceType="Patient",
                    identifier=[{
                        "use": "usual",
                        "system": "http://hospital.medai.com/patients",
                        "value": "12345"
                    }],
                    name=[{
                        "use": "usual",
                        "family": "Silva",
                        "given": ["João"]
                    }],
                    gender="male",
                    active=True
                )]
            
            telemetry.record_fhir_operation("Patient", "search", True)
            logger.info("FHIR Patient search completed", extra={
                "search_params": {
                    "family": family,
                    "given": given,
                    "identifier": identifier
                },
                "result_count": len(results)
            })
            
            return results
            
        except Exception as e:
            telemetry.record_fhir_operation("Patient", "search", False)
            logger.error(f"Failed to search FHIR Patients: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "FHIR_SEARCH_ERROR",
                    "message": "Failed to search FHIR Patient resources",
                    "details": {}
                }
            )


@router.get("/metadata")
async def get_capability_statement():
    """
    Get FHIR Capability Statement (server metadata)
    
    Returns:
        FHIR Capability Statement
    """
    with telemetry.create_span("fhir.metadata") as span:
        capability_statement = {
            "resourceType": "CapabilityStatement",
            "id": "medai-fhir-server",
            "version": "1.0.0",
            "name": "MedAI FHIR Server",
            "title": "MedAI FHIR R4 Server",
            "status": "active",
            "date": "2024-01-01",
            "publisher": "MedAI",
            "description": "FHIR R4 server for MedAI healthcare platform",
            "kind": "instance",
            "software": {
                "name": "MedAI FHIR Server",
                "version": "1.0.0"
            },
            "implementation": {
                "description": "MedAI FHIR R4 implementation",
                "url": "https://api.medai.com/fhir"
            },
            "fhirVersion": "4.0.1",
            "format": ["json"],
            "rest": [
                {
                    "mode": "server",
                    "documentation": "Main FHIR endpoint",
                    "security": {
                        "cors": True,
                        "description": "OAuth2 Bearer Token authentication"
                    },
                    "resource": [
                        {
                            "type": "Patient",
                            "profile": "http://hl7.org/fhir/StructureDefinition/Patient",
                            "interaction": [
                                {"code": "create"},
                                {"code": "read"},
                                {"code": "search-type"}
                            ],
                            "searchParam": [
                                {
                                    "name": "family",
                                    "type": "string",
                                    "documentation": "A portion of the family name of the patient"
                                },
                                {
                                    "name": "given",
                                    "type": "string", 
                                    "documentation": "A portion of the given name of the patient"
                                },
                                {
                                    "name": "identifier",
                                    "type": "token",
                                    "documentation": "A patient identifier"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        span.set_attributes({
            "fhir.operation": "metadata",
            "fhir.version": "4.0.1"
        })
        
        return capability_statement