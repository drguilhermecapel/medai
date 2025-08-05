"""
Multi-Specialty EMR Service Usage Example

This example demonstrates how to use the MultiSpecialtyEMRService
for coordinating care between multiple medical specialties.
"""

import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

# This would normally be imported from the actual service
# from app.services.multi_specialty_emr import MultiSpecialtyEMRService, MedicalSpecialty, ConsultationType

# For demonstration purposes, we'll use mock classes
class MockAsyncSession:
    """Mock database session for demonstration."""
    pass

# Import the enums we defined
from enum import Enum

class MedicalSpecialty(str, Enum):
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    ONCOLOGY = "oncology"
    ORTHOPEDICS = "orthopedics"
    ENDOCRINOLOGY = "endocrinology"
    # ... other specialties

class ConsultationType(str, Enum):
    REFERRAL = "referral"
    SECOND_OPINION = "second_opinion"
    COLLABORATIVE = "collaborative" 
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"

async def demonstrate_multi_specialty_workflow():
    """
    Demonstrate a complete multi-specialty EMR workflow.
    """
    print("🏥 Multi-Specialty EMR Service Demonstration")
    print("=" * 50)
    
    # Initialize service (in real usage, this would use actual database session)
    db_session = MockAsyncSession()
    # service = MultiSpecialtyEMRService(db_session)
    
    # Sample patient and physician IDs
    patient_id = uuid4()
    cardiology_physician_id = uuid4()
    neurology_physician_id = uuid4()
    endocrinology_physician_id = uuid4()
    
    print(f"👤 Patient ID: {patient_id}")
    print(f"👨‍⚕️ Cardiology Physician: {cardiology_physician_id}")
    print(f"👨‍⚕️ Neurology Physician: {neurology_physician_id}")
    print(f"👨‍⚕️ Endocrinology Physician: {endocrinology_physician_id}")
    print()
    
    # 1. Create Multi-Specialty Case
    print("1️⃣ Creating Multi-Specialty Case")
    print("-" * 30)
    
    case_data = {
        "patient_id": patient_id,
        "primary_specialty": MedicalSpecialty.CARDIOLOGY,
        "primary_physician_id": cardiology_physician_id,
        "involved_specialties": [MedicalSpecialty.NEUROLOGY, MedicalSpecialty.ENDOCRINOLOGY],
        "case_description": "62-year-old patient with cardiac arrhythmia, diabetes, and recent syncope episodes requiring coordinated multi-specialty care",
        "consultation_type": ConsultationType.COLLABORATIVE,
        "priority": "high"
    }
    
    print(f"📋 Case: {case_data['case_description']}")
    print(f"🏥 Primary Specialty: {case_data['primary_specialty'].value}")
    print(f"👥 Involved Specialties: {[s.value for s in case_data['involved_specialties']]}")
    print(f"⚡ Priority: {case_data['priority']}")
    print()
    
    # In real usage: case = await service.create_multi_specialty_case(**case_data)
    case_id = uuid4()
    print(f"✅ Multi-specialty case created with ID: {case_id}")
    print()
    
    # 2. Schedule Cross-Specialty Consultations
    print("2️⃣ Scheduling Cross-Specialty Consultations")
    print("-" * 40)
    
    # Schedule neurology consultation
    neuro_consultation = {
        "case_id": case_id,
        "consulting_specialty": MedicalSpecialty.NEUROLOGY,
        "consulting_physician_id": neurology_physician_id,
        "scheduled_datetime": datetime.now() + timedelta(days=2),
        "consultation_notes": "Evaluate syncope episodes, rule out seizure activity, assess for cardiac-neurologic interactions"
    }
    
    print(f"🧠 Neurology Consultation:")
    print(f"   📅 Scheduled: {neuro_consultation['scheduled_datetime'].strftime('%Y-%m-%d %H:%M')}")
    print(f"   📝 Notes: {neuro_consultation['consultation_notes']}")
    print()
    
    # Schedule endocrinology consultation
    endo_consultation = {
        "case_id": case_id,
        "consulting_specialty": MedicalSpecialty.ENDOCRINOLOGY,
        "consulting_physician_id": endocrinology_physician_id,
        "scheduled_datetime": datetime.now() + timedelta(days=1),
        "consultation_notes": "Optimize diabetes management, assess impact on cardiac condition, coordinate medication interactions"
    }
    
    print(f"🔬 Endocrinology Consultation:")
    print(f"   📅 Scheduled: {endo_consultation['scheduled_datetime'].strftime('%Y-%m-%d %H:%M')}")
    print(f"   📝 Notes: {endo_consultation['consultation_notes']}")
    print()
    
    # In real usage:
    # neuro_appointment = await service.schedule_cross_specialty_consultation(**neuro_consultation)
    # endo_appointment = await service.schedule_cross_specialty_consultation(**endo_consultation)
    
    # 3. Create Coordinated Care Plan
    print("3️⃣ Creating Coordinated Care Plan")
    print("-" * 32)
    
    care_plan_data = {
        "case_id": case_id,
        "care_plan_data": {
            "goals": [
                "Stabilize cardiac arrhythmia",
                "Optimize diabetes management", 
                "Identify and prevent syncope episodes",
                "Coordinate medication regimen",
                "Improve overall quality of life"
            ],
            "interventions": {
                "cardiology": [
                    "Continuous cardiac monitoring",
                    "Adjust antiarrhythmic medications",
                    "Assess need for device therapy",
                    "Monitor drug interactions"
                ],
                "neurology": [
                    "EEG monitoring for seizure activity",
                    "Neurological examination",
                    "Cognitive assessment",
                    "Syncope workup"
                ],
                "endocrinology": [
                    "Optimize insulin regimen",
                    "Monitor HbA1c levels",
                    "Assess diabetic complications",
                    "Coordinate with cardiac medications"
                ]
            },
            "coordination_points": [
                "Weekly multidisciplinary team meetings",
                "Shared medication review sessions",
                "Joint interpretation of monitoring results",
                "Coordinated patient education sessions"
            ],
            "timelines": {
                "acute_stabilization": "1-2 weeks",
                "optimization_phase": "4-6 weeks",
                "maintenance_phase": "ongoing",
                "next_review": "3 months"
            },
            "success_metrics": [
                "Arrhythmia episodes reduced by 50%",
                "HbA1c < 7.0%",
                "No syncope episodes for 30 days",
                "Patient satisfaction score > 8/10",
                "Zero medication conflicts"
            ]
        },
        "created_by": cardiology_physician_id
    }
    
    print("🎯 Care Plan Goals:")
    for i, goal in enumerate(care_plan_data["care_plan_data"]["goals"], 1):
        print(f"   {i}. {goal}")
    print()
    
    print("🏥 Specialty Interventions:")
    for specialty, interventions in care_plan_data["care_plan_data"]["interventions"].items():
        print(f"   {specialty.title()}:")
        for intervention in interventions:
            print(f"     • {intervention}")
    print()
    
    print("🤝 Coordination Points:")
    for point in care_plan_data["care_plan_data"]["coordination_points"]:
        print(f"   • {point}")
    print()
    
    print("📊 Success Metrics:")
    for metric in care_plan_data["care_plan_data"]["success_metrics"]:
        print(f"   ✓ {metric}")
    print()
    
    # In real usage: care_plan = await service.create_coordinated_care_plan(**care_plan_data)
    care_plan_id = uuid4()
    print(f"✅ Coordinated care plan created with ID: {care_plan_id}")
    print()
    
    # 4. Patient Specialty History
    print("4️⃣ Patient Specialty History")
    print("-" * 26)
    
    # In real usage: history = await service.get_patient_specialty_history(patient_id)
    
    # Mock history data for demonstration
    mock_history = {
        "patient_id": str(patient_id),
        "specialty_history": {
            "cardiology": {
                "appointments": 3,
                "latest_diagnosis": "Atrial fibrillation with rapid ventricular response",
                "current_medications": ["Metoprolol", "Warfarin", "Digoxin"],
                "last_visit": "2024-01-15"
            },
            "endocrinology": {
                "appointments": 2,
                "latest_diagnosis": "Type 2 Diabetes Mellitus, poorly controlled",
                "current_medications": ["Metformin", "Insulin glargine"],
                "last_visit": "2024-01-10"
            },
            "neurology": {
                "appointments": 1,
                "latest_diagnosis": "Syncope, etiology to be determined",
                "current_medications": [],
                "last_visit": "2024-01-05"
            }
        },
        "multi_specialty_cases": [
            {
                "case_id": str(case_id),
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "involved_specialties": ["cardiology", "neurology", "endocrinology"]
            }
        ]
    }
    
    print("📊 Specialty Visit Summary:")
    for specialty, data in mock_history["specialty_history"].items():
        print(f"   {specialty.title()}:")
        print(f"     • Appointments: {data['appointments']}")
        print(f"     • Latest Diagnosis: {data['latest_diagnosis']}")
        print(f"     • Last Visit: {data['last_visit']}")
    print()
    
    print(f"📋 Active Multi-Specialty Cases: {len(mock_history['multi_specialty_cases'])}")
    print()
    
    # 5. Case Status Summary
    print("5️⃣ Case Status Summary")
    print("-" * 21)
    
    print(f"📅 Case Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"🏥 Primary Specialty: Cardiology")
    print(f"👥 Consulting Specialties: Neurology, Endocrinology") 
    print(f"📋 Consultations Scheduled: 2")
    print(f"📝 Care Plan: Active")
    print(f"⏰ Next Milestone: Neurology consultation in 1 day")
    print()
    
    print("🎉 Multi-Specialty EMR Workflow Complete!")
    print("=" * 50)
    
    return {
        "case_id": case_id,
        "care_plan_id": care_plan_id,
        "consultations_scheduled": 2,
        "specialties_involved": 3
    }

def demonstrate_specialty_transfer():
    """
    Demonstrate transferring a case between specialties.
    """
    print("\n🔄 Specialty Transfer Demonstration")
    print("-" * 35)
    
    case_id = uuid4()
    original_physician = uuid4()
    new_physician = uuid4()
    
    print(f"📋 Case ID: {case_id}")
    print(f"🔄 Transfer: Internal Medicine → Endocrinology")
    print(f"👨‍⚕️ Original Physician: {original_physician}")
    print(f"👨‍⚕️ New Physician: {new_physician}")
    print()
    
    transfer_data = {
        "case_id": case_id,
        "new_primary_specialty": MedicalSpecialty.ENDOCRINOLOGY,
        "new_primary_physician_id": new_physician,
        "transfer_reason": "Complex diabetes management requiring specialized endocrine expertise",
        "transferred_by": original_physician
    }
    
    print(f"📝 Transfer Reason: {transfer_data['transfer_reason']}")
    print()
    
    # In real usage: updated_case = await service.transfer_case_specialty(**transfer_data)
    
    print("✅ Case successfully transferred to Endocrinology")
    print("📧 Notifications sent to both physicians")
    print("📄 Transfer documented in audit log")
    print()

async def main():
    """Run the complete demonstration."""
    # Run main workflow demonstration
    workflow_result = await demonstrate_multi_specialty_workflow()
    
    # Run specialty transfer demonstration
    demonstrate_specialty_transfer()
    
    # Final summary
    print("📈 Demonstration Summary:")
    print(f"   • Cases created: 1")
    print(f"   • Specialties coordinated: {workflow_result['specialties_involved']}")
    print(f"   • Consultations scheduled: {workflow_result['consultations_scheduled']}")
    print(f"   • Care plans created: 1")
    print(f"   • Case transfers: 1")
    print()
    print("🎯 The multi-specialty EMR system enables seamless coordination")
    print("   between medical specialties for optimal patient care!")

if __name__ == "__main__":
    asyncio.run(main())