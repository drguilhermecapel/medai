"""
Multi-Specialty EMR Service - Comprehensive multi-specialty electronic medical record management.

This service handles coordination between multiple medical specialties for patient care,
including cross-specialty consultations, referrals, and coordinated treatment plans.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import AppointmentStatus, UserRole, MedicalSpecialty
from app.models.appointment import Appointment
from app.models.doctor_profile import DoctorProfile
from app.models.patient import Patient
from app.models.user import User
from app.services.base import BaseService
from app.services.medical_record_service import MedicalRecordService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class ConsultationType(str, Enum):
    """Types of multi-specialty consultations."""
    REFERRAL = "referral"
    SECOND_OPINION = "second_opinion"
    COLLABORATIVE = "collaborative" 
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"


class CoordinationStatus(str, Enum):
    """Status of multi-specialty coordination."""
    INITIATED = "initiated"
    PENDING_RESPONSE = "pending_response"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class MultiSpecialtyCase:
    """Represents a case involving multiple medical specialties."""
    
    def __init__(
        self,
        case_id: UUID,
        patient_id: UUID,
        primary_specialty: MedicalSpecialty,
        primary_physician_id: UUID,
        involved_specialties: List[MedicalSpecialty],
        case_description: str,
        status: CoordinationStatus = CoordinationStatus.INITIATED,
        created_at: datetime = None
    ):
        self.case_id = case_id
        self.patient_id = patient_id
        self.primary_specialty = primary_specialty
        self.primary_physician_id = primary_physician_id
        self.involved_specialties = involved_specialties
        self.case_description = case_description
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.consultations: List[Dict[str, Any]] = []
        self.care_plan: Dict[str, Any] = {}
        self.notes: List[Dict[str, Any]] = []


class MultiSpecialtyEMRService(BaseService):
    """
    Service for managing multi-specialty electronic medical record workflows.
    
    Provides functionality for:
    - Cross-specialty patient case coordination
    - Referral management
    - Multi-specialty care planning
    - Consultation scheduling and tracking
    - Specialty-specific EMR access controls
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.medical_record_service = MedicalRecordService(db)
        self.notification_service = NotificationService(db)
        self.active_cases: Dict[UUID, MultiSpecialtyCase] = {}

    async def create_multi_specialty_case(
        self,
        patient_id: UUID,
        primary_specialty: MedicalSpecialty,
        primary_physician_id: UUID,
        involved_specialties: List[MedicalSpecialty],
        case_description: str,
        consultation_type: ConsultationType = ConsultationType.REFERRAL,
        priority: str = "normal",
        requested_by: UUID = None
    ) -> MultiSpecialtyCase:
        """
        Create a new multi-specialty case for coordinated patient care.
        
        Args:
            patient_id: ID of the patient
            primary_specialty: Primary medical specialty handling the case
            primary_physician_id: ID of the primary physician
            involved_specialties: List of specialties to be involved
            case_description: Description of the case and coordination needs
            consultation_type: Type of multi-specialty consultation
            priority: Priority level (low, normal, high, urgent)
            requested_by: ID of the user requesting the coordination
        
        Returns:
            MultiSpecialtyCase: The created case
        """
        try:
            case_id = uuid4()
            
            # Validate patient exists
            patient = await self._get_patient(patient_id)
            if not patient:
                raise ValueError(f"Patient with ID {patient_id} not found")
            
            # Validate primary physician
            primary_physician = await self._get_physician(primary_physician_id)
            if not primary_physician:
                raise ValueError(f"Physician with ID {primary_physician_id} not found")
            
            # Create the multi-specialty case
            case = MultiSpecialtyCase(
                case_id=case_id,
                patient_id=patient_id,
                primary_specialty=primary_specialty,
                primary_physician_id=primary_physician_id,
                involved_specialties=involved_specialties,
                case_description=case_description
            )
            
            # Store case in active cases
            self.active_cases[case_id] = case
            
            # Log case creation
            await self.log_audit(
                user_id=requested_by or primary_physician_id,
                action="create_multi_specialty_case",
                resource_type="multi_specialty_case",
                resource_id=case_id,
                description=f"Created multi-specialty case for patient {patient_id}",
                metadata={
                    "primary_specialty": primary_specialty.value,
                    "involved_specialties": [s.value for s in involved_specialties],
                    "consultation_type": consultation_type.value,
                    "priority": priority
                }
            )
            
            # Notify involved specialties
            await self._notify_involved_specialties(case, consultation_type, priority)
            
            logger.info(f"Created multi-specialty case {case_id} for patient {patient_id}")
            
            return case
            
        except Exception as e:
            logger.error(f"Error creating multi-specialty case: {e}")
            raise

    async def get_specialty_physicians(
        self,
        specialty: MedicalSpecialty,
        available_only: bool = False,
        hospital_filter: Optional[str] = None
    ) -> List[DoctorProfile]:
        """
        Get physicians by specialty with optional filtering.
        
        Args:
            specialty: Medical specialty to filter by
            available_only: If True, only return currently available physicians
            hospital_filter: Optional hospital name to filter by
        
        Returns:
            List[DoctorProfile]: List of physicians in the specialty
        """
        try:
            query = select(DoctorProfile).options(selectinload(DoctorProfile.user))
            
            # Filter by specialty
            conditions = [DoctorProfile.specialties.contains([specialty.value])]
            
            # Add hospital filter if provided
            if hospital_filter:
                conditions.append(DoctorProfile.current_hospital == hospital_filter)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await self.db.execute(query)
            physicians = result.scalars().all()
            
            # If available_only is True, filter by current availability
            if available_only:
                physicians = await self._filter_available_physicians(physicians)
            
            return physicians
            
        except Exception as e:
            logger.error(f"Error getting specialty physicians: {e}")
            raise

    async def schedule_cross_specialty_consultation(
        self,
        case_id: UUID,
        consulting_specialty: MedicalSpecialty,
        consulting_physician_id: UUID,
        scheduled_datetime: datetime,
        consultation_notes: Optional[str] = None,
        requested_by: UUID = None
    ) -> Appointment:
        """
        Schedule a consultation between specialties for a multi-specialty case.
        
        Args:
            case_id: ID of the multi-specialty case
            consulting_specialty: Specialty providing the consultation
            consulting_physician_id: ID of the consulting physician
            scheduled_datetime: When the consultation is scheduled
            consultation_notes: Optional notes about the consultation
            requested_by: ID of the user requesting the consultation
        
        Returns:
            Appointment: The scheduled consultation appointment
        """
        try:
            # Get the case
            case = self.active_cases.get(case_id)
            if not case:
                raise ValueError(f"Multi-specialty case {case_id} not found")
            
            # Validate consulting physician
            consulting_physician = await self._get_physician(consulting_physician_id)
            if not consulting_physician:
                raise ValueError(f"Consulting physician {consulting_physician_id} not found")
            
            # Create appointment code
            appointment_code = f"MSC-{case_id.hex[:8]}-{consulting_specialty.value.upper()}"
            
            # Create the consultation appointment
            appointment = Appointment(
                appointment_code=appointment_code,
                patient_id=case.patient_id,
                physician_id=consulting_physician_id,
                scheduled_by_id=requested_by or case.primary_physician_id,
                title=f"Multi-Specialty Consultation - {consulting_specialty.value.title()}",
                appointment_type="multi_specialty_consultation",
                specialty=consulting_specialty.value,
                scheduled_datetime=scheduled_datetime,
                duration_minutes=60,  # Default duration
                status=AppointmentStatus.SCHEDULED.value,
                notes=consultation_notes or "",
                metadata={
                    "multi_specialty_case_id": str(case_id),
                    "consultation_type": "cross_specialty",
                    "primary_specialty": case.primary_specialty.value,
                    "primary_physician_id": str(case.primary_physician_id)
                }
            )
            
            # Save appointment
            self.db.add(appointment)
            await self.db.commit()
            await self.db.refresh(appointment)
            
            # Add consultation to case
            consultation_info = {
                "appointment_id": appointment.id,
                "specialty": consulting_specialty.value,
                "physician_id": consulting_physician_id,
                "scheduled_datetime": scheduled_datetime.isoformat(),
                "status": "scheduled",
                "notes": consultation_notes or ""
            }
            case.consultations.append(consultation_info)
            
            # Log consultation scheduling
            await self.log_audit(
                user_id=requested_by or case.primary_physician_id,
                action="schedule_cross_specialty_consultation",
                resource_type="appointment",
                resource_id=appointment.id,
                description=f"Scheduled {consulting_specialty.value} consultation for case {case_id}",
                metadata={
                    "case_id": str(case_id),
                    "consulting_specialty": consulting_specialty.value,
                    "scheduled_datetime": scheduled_datetime.isoformat()
                }
            )
            
            # Send notifications
            await self._notify_consultation_scheduled(case, appointment, consulting_physician)
            
            logger.info(f"Scheduled cross-specialty consultation {appointment.id} for case {case_id}")
            
            return appointment
            
        except Exception as e:
            logger.error(f"Error scheduling cross-specialty consultation: {e}")
            raise

    async def create_coordinated_care_plan(
        self,
        case_id: UUID,
        care_plan_data: Dict[str, Any],
        created_by: UUID
    ) -> Dict[str, Any]:
        """
        Create a coordinated care plan involving multiple specialties.
        
        Args:
            case_id: ID of the multi-specialty case
            care_plan_data: Care plan details including goals, interventions, and timelines
            created_by: ID of the user creating the care plan
        
        Returns:
            Dict[str, Any]: The created care plan
        """
        try:
            # Get the case
            case = self.active_cases.get(case_id)
            if not case:
                raise ValueError(f"Multi-specialty case {case_id} not found")
            
            # Create care plan with coordination elements
            care_plan = {
                "plan_id": str(uuid4()),
                "case_id": str(case_id),
                "patient_id": str(case.patient_id),
                "primary_specialty": case.primary_specialty.value,
                "involved_specialties": [s.value for s in case.involved_specialties],
                "created_by": str(created_by),
                "created_at": datetime.utcnow().isoformat(),
                "goals": care_plan_data.get("goals", []),
                "interventions": care_plan_data.get("interventions", {}),
                "timelines": care_plan_data.get("timelines", {}),
                "coordination_points": care_plan_data.get("coordination_points", []),
                "follow_up_schedule": care_plan_data.get("follow_up_schedule", {}),
                "success_metrics": care_plan_data.get("success_metrics", []),
                "contingency_plans": care_plan_data.get("contingency_plans", {}),
                "status": "active"
            }
            
            # Add care plan to case
            case.care_plan = care_plan
            
            # Log care plan creation
            await self.log_audit(
                user_id=created_by,
                action="create_coordinated_care_plan",
                resource_type="care_plan",
                resource_id=UUID(care_plan["plan_id"]),
                description=f"Created coordinated care plan for multi-specialty case {case_id}",
                metadata={
                    "case_id": str(case_id),
                    "involved_specialties": care_plan["involved_specialties"],
                    "goals_count": len(care_plan["goals"])
                }
            )
            
            # Notify involved specialties about the care plan
            await self._notify_care_plan_created(case, care_plan)
            
            logger.info(f"Created coordinated care plan {care_plan['plan_id']} for case {case_id}")
            
            return care_plan
            
        except Exception as e:
            logger.error(f"Error creating coordinated care plan: {e}")
            raise

    async def get_patient_specialty_history(
        self,
        patient_id: UUID,
        specialty: Optional[MedicalSpecialty] = None,
        include_referrals: bool = True
    ) -> Dict[str, Any]:
        """
        Get a patient's history across specialties or within a specific specialty.
        
        Args:
            patient_id: ID of the patient
            specialty: Optional specific specialty to filter by
            include_referrals: Whether to include referral information
        
        Returns:
            Dict[str, Any]: Patient's specialty history
        """
        try:
            # Get patient
            patient = await self._get_patient(patient_id)
            if not patient:
                raise ValueError(f"Patient with ID {patient_id} not found")
            
            # Build query for appointments
            query = select(Appointment).where(Appointment.patient_id == patient_id)
            
            if specialty:
                query = query.where(Appointment.specialty == specialty.value)
            
            # Order by date
            query = query.order_by(Appointment.scheduled_datetime.desc())
            
            result = await self.db.execute(query)
            appointments = result.scalars().all()
            
            # Organize history by specialty
            specialty_history = {}
            
            for appointment in appointments:
                app_specialty = appointment.specialty or "general"
                
                if app_specialty not in specialty_history:
                    specialty_history[app_specialty] = {
                        "specialty": app_specialty,
                        "appointments": [],
                        "diagnoses": [],
                        "treatments": [],
                        "referrals": []
                    }
                
                appointment_data = {
                    "id": str(appointment.id),
                    "date": appointment.scheduled_datetime.isoformat(),
                    "physician_id": str(appointment.physician_id) if appointment.physician_id else None,
                    "type": appointment.appointment_type,
                    "status": appointment.status,
                    "notes": appointment.notes,
                    "diagnosis": appointment.diagnosis,
                    "treatment_notes": appointment.treatment_notes
                }
                
                specialty_history[app_specialty]["appointments"].append(appointment_data)
                
                # Extract diagnoses and treatments
                if appointment.diagnosis:
                    specialty_history[app_specialty]["diagnoses"].append({
                        "diagnosis": appointment.diagnosis,
                        "date": appointment.scheduled_datetime.isoformat(),
                        "appointment_id": str(appointment.id)
                    })
                
                if appointment.treatment_notes:
                    specialty_history[app_specialty]["treatments"].append({
                        "treatment": appointment.treatment_notes,
                        "date": appointment.scheduled_datetime.isoformat(),
                        "appointment_id": str(appointment.id)
                    })
            
            # Add multi-specialty case information
            patient_cases = [case for case in self.active_cases.values() 
                           if case.patient_id == patient_id]
            
            return {
                "patient_id": str(patient_id),
                "specialty_history": specialty_history,
                "multi_specialty_cases": [
                    {
                        "case_id": str(case.case_id),
                        "primary_specialty": case.primary_specialty.value,
                        "involved_specialties": [s.value for s in case.involved_specialties],
                        "status": case.status.value,
                        "created_at": case.created_at.isoformat(),
                        "description": case.case_description,
                        "consultations_count": len(case.consultations)
                    }
                    for case in patient_cases
                ],
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting patient specialty history: {e}")
            raise

    async def transfer_case_specialty(
        self,
        case_id: UUID,
        new_primary_specialty: MedicalSpecialty,
        new_primary_physician_id: UUID,
        transfer_reason: str,
        transferred_by: UUID
    ) -> MultiSpecialtyCase:
        """
        Transfer primary responsibility of a case to a different specialty.
        
        Args:
            case_id: ID of the case to transfer
            new_primary_specialty: New primary specialty
            new_primary_physician_id: ID of the new primary physician
            transfer_reason: Reason for the transfer
            transferred_by: ID of the user performing the transfer
        
        Returns:
            MultiSpecialtyCase: The updated case
        """
        try:
            # Get the case
            case = self.active_cases.get(case_id)
            if not case:
                raise ValueError(f"Multi-specialty case {case_id} not found")
            
            # Validate new primary physician
            new_physician = await self._get_physician(new_primary_physician_id)
            if not new_physician:
                raise ValueError(f"New primary physician {new_primary_physician_id} not found")
            
            # Store previous information for audit
            previous_specialty = case.primary_specialty
            previous_physician_id = case.primary_physician_id
            
            # Update case
            case.primary_specialty = new_primary_specialty
            case.primary_physician_id = new_primary_physician_id
            
            # Add transfer note
            transfer_note = {
                "note_id": str(uuid4()),
                "type": "transfer",
                "created_by": str(transferred_by),
                "created_at": datetime.utcnow().isoformat(),
                "content": f"Case transferred from {previous_specialty.value} to {new_primary_specialty.value}",
                "reason": transfer_reason,
                "previous_physician": str(previous_physician_id),
                "new_physician": str(new_primary_physician_id)
            }
            case.notes.append(transfer_note)
            
            # Log transfer
            await self.log_audit(
                user_id=transferred_by,
                action="transfer_case_specialty",
                resource_type="multi_specialty_case",
                resource_id=case_id,
                description=f"Transferred case from {previous_specialty.value} to {new_primary_specialty.value}",
                metadata={
                    "previous_specialty": previous_specialty.value,
                    "new_specialty": new_primary_specialty.value,
                    "previous_physician": str(previous_physician_id),
                    "new_physician": str(new_primary_physician_id),
                    "reason": transfer_reason
                }
            )
            
            # Notify both old and new physicians
            await self._notify_case_transfer(case, previous_physician_id, new_physician, transfer_reason)
            
            logger.info(f"Transferred case {case_id} from {previous_specialty.value} to {new_primary_specialty.value}")
            
            return case
            
        except Exception as e:
            logger.error(f"Error transferring case specialty: {e}")
            raise

    # Private helper methods

    async def _get_patient(self, patient_id: UUID) -> Optional[Patient]:
        """Get patient by ID."""
        query = select(Patient).where(Patient.id == patient_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_physician(self, physician_id: UUID) -> Optional[User]:
        """Get physician by ID."""
        query = select(User).options(selectinload(User.doctor_profile)).where(
            and_(User.id == physician_id, User.role == UserRole.DOCTOR)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _filter_available_physicians(self, physicians: List[DoctorProfile]) -> List[DoctorProfile]:
        """Filter physicians by current availability."""
        # This would typically check scheduling, working hours, etc.
        # For now, return all physicians (placeholder implementation)
        return physicians

    async def _notify_involved_specialties(
        self,
        case: MultiSpecialtyCase,
        consultation_type: ConsultationType,
        priority: str
    ):
        """Send notifications to involved specialties about new case."""
        # Placeholder for notification logic
        logger.info(f"Notifying involved specialties for case {case.case_id}")

    async def _notify_consultation_scheduled(
        self,
        case: MultiSpecialtyCase,
        appointment: Appointment,
        consulting_physician: User
    ):
        """Send notifications about scheduled consultation."""
        # Placeholder for notification logic
        logger.info(f"Notifying about consultation {appointment.id} for case {case.case_id}")

    async def _notify_care_plan_created(self, case: MultiSpecialtyCase, care_plan: Dict[str, Any]):
        """Send notifications about new care plan."""
        # Placeholder for notification logic
        logger.info(f"Notifying about care plan {care_plan['plan_id']} for case {case.case_id}")

    async def _notify_case_transfer(
        self,
        case: MultiSpecialtyCase,
        previous_physician_id: UUID,
        new_physician: User,
        transfer_reason: str
    ):
        """Send notifications about case transfer."""
        # Placeholder for notification logic
        logger.info(f"Notifying about case transfer {case.case_id}")