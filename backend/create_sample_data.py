"""
Sample data generator for multi-specialty EHR system
Creates demo patients and clinical data for testing
"""
import asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models.base import Base
from app.models.patient import Patient
from app.models.user import User
from app.models.fhir_base import FHIRPatient, FHIREncounter, FHIRCondition, FHIRObservation
from app.models.specialties.dermatology import DermatologyLesion, DermatologyExamination
from app.models.specialties.pediatrics import PediatricsGrowthChart, PediatricsVaccination


def create_sample_patients(db: Session):
    """Create sample patients for testing"""
    
    # Sample patient data
    patients_data = [
        {
            "first_name": "Maria",
            "last_name": "Silva",
            "email": "maria.silva@email.com",
            "birth_date": date(1985, 3, 15),
            "gender": "female",
            "cpf": "123.456.789-01",
            "specialty": "dermatology"
        },
        {
            "first_name": "João",
            "last_name": "Santos",
            "email": "joao.santos@email.com", 
            "birth_date": date(1978, 8, 22),
            "gender": "male",
            "cpf": "987.654.321-09",
            "specialty": "dermatology"
        },
        {
            "first_name": "Ana",
            "last_name": "Costa",
            "email": "ana.costa@email.com",
            "birth_date": date(1990, 12, 5),
            "gender": "female", 
            "cpf": "456.789.123-45",
            "specialty": "dermatology"
        },
        {
            "first_name": "Pedro",
            "last_name": "Oliveira",
            "email": "pedro.oliveira@email.com",
            "birth_date": date(2020, 4, 10),
            "gender": "male",
            "cpf": "789.123.456-78",
            "specialty": "pediatrics"
        },
        {
            "first_name": "Sofia",
            "last_name": "Mendes",
            "email": "sofia.mendes@email.com",
            "birth_date": date(2019, 7, 18),
            "gender": "female",
            "cpf": "321.654.987-32",
            "specialty": "pediatrics"
        },
        {
            "first_name": "Lucas",
            "last_name": "Ferreira",
            "email": "lucas.ferreira@email.com",
            "birth_date": date(2021, 1, 25),
            "gender": "male", 
            "cpf": "654.987.321-65",
            "specialty": "pediatrics"
        }
    ]
    
    created_patients = []
    
    for patient_data in patients_data:
        # Create user first
        user = User(
            id=uuid4(),
            first_name=patient_data["first_name"],
            last_name=patient_data["last_name"],
            email=patient_data["email"],
            username=patient_data["email"],
            role="patient",
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Create patient
        patient = Patient(
            user_id=user.id,
            birth_date=patient_data["birth_date"],
            gender=patient_data["gender"],
            cpf=patient_data["cpf"],
            medical_record_number=f"MED{2024}{str(len(created_patients)+1).zfill(6)}",
            is_active_patient=True
        )
        db.add(patient)
        db.flush()
        
        # Create FHIR Patient
        fhir_patient = FHIRPatient(
            patient_id=patient.id,
            active=True,
            name=[{
                "use": "official",
                "family": patient_data["last_name"],
                "given": [patient_data["first_name"]]
            }],
            gender=patient_data["gender"],
            birth_date=patient_data["birth_date"]
        )
        db.add(fhir_patient)
        db.flush()
        
        created_patients.append({
            "patient": patient,
            "fhir_patient": fhir_patient,
            "specialty": patient_data["specialty"]
        })
    
    return created_patients


def create_dermatology_sample_data(db: Session, patients):
    """Create sample dermatology data"""
    
    dermatology_patients = [p for p in patients if p["specialty"] == "dermatology"]
    
    for patient_data in dermatology_patients:
        fhir_patient = patient_data["fhir_patient"]
        
        # Create examination
        fhir_observation = FHIRObservation(
            patient_id=fhir_patient.id,
            status="final",
            category=[{"coding": [{"code": "exam", "system": "http://terminology.hl7.org/CodeSystem/observation-category"}]}],
            code={"coding": [{"code": "5880005", "system": "http://snomed.info/sct", "display": "Physical examination procedure"}]},
            subject=f"Patient/{fhir_patient.patient_id}",
            effective_datetime=datetime.now() - timedelta(days=30),
            specialty_data={"specialty": "dermatology", "examination_type": "full_body"}
        )
        db.add(fhir_observation)
        db.flush()
        
        examination = DermatologyExamination(
            fhir_observation_id=fhir_observation.id,
            examination_type="full_body",
            examination_scope=["head", "neck", "trunk", "arms", "legs"],
            fitzpatrick_skin_type="III",
            sun_exposure_history={"childhood_sunburns": True, "outdoor_work": False},
            sunscreen_use="regular",
            family_history_skin_cancer=False,
            total_moles_count=25,
            atypical_moles_count=2,
            overall_skin_condition="good",
            risk_stratification="low",
            recommendations=["Annual skin check", "Daily sunscreen use"],
            next_examination_interval=12,
            total_photos_taken=15,
            body_map_created=True
        )
        db.add(examination)
        
        # Create lesions with varying ABCDE scores
        lesion_data_sets = [
            {
                "lesion_type": "melanocytic_nevus",
                "anatomical_location": "left_shoulder",
                "body_region": "trunk",
                "abcde_scores": {"asymmetry": 0, "border": 0, "color": 0, "diameter": 1, "evolving": 0},
                "risk": "low"
            },
            {
                "lesion_type": "atypical_nevus", 
                "anatomical_location": "right_calf",
                "body_region": "leg",
                "abcde_scores": {"asymmetry": 1, "border": 1, "color": 1, "diameter": 1, "evolving": 0},
                "risk": "moderate"
            },
            {
                "lesion_type": "suspicious_lesion",
                "anatomical_location": "forehead",
                "body_region": "head",
                "abcde_scores": {"asymmetry": 2, "border": 2, "color": 1, "diameter": 2, "evolving": 1},
                "risk": "high"
            }
        ]
        
        for lesion_data in lesion_data_sets:
            # Create FHIR Condition
            fhir_condition = FHIRCondition(
                patient_id=fhir_patient.id,
                clinical_status={"coding": [{"code": "active", "system": "http://terminology.hl7.org/CodeSystem/condition-clinical"}]},
                verification_status={"coding": [{"code": "confirmed", "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status"}]},
                category=[{"coding": [{"code": "problem-list-item", "system": "http://terminology.hl7.org/CodeSystem/condition-category"}]}],
                code={"coding": [{"code": "400006008", "system": "http://snomed.info/sct", "display": "Skin lesion"}]},
                subject=f"Patient/{fhir_patient.patient_id}",
                specialty_data={"specialty": "dermatology", "lesion_type": lesion_data["lesion_type"]}
            )
            db.add(fhir_condition)
            db.flush()
            
            # Calculate ABCDE scores
            scores = lesion_data["abcde_scores"]
            total_score = sum(scores.values())
            
            lesion = DermatologyLesion(
                fhir_condition_id=fhir_condition.id,
                lesion_type=lesion_data["lesion_type"],
                anatomical_location=lesion_data["anatomical_location"],
                body_region=lesion_data["body_region"],
                abcde_asymmetry="symmetric" if scores["asymmetry"] == 0 else "asymmetric",
                abcde_asymmetry_score=Decimal(str(scores["asymmetry"])),
                abcde_border="regular" if scores["border"] == 0 else "irregular",
                abcde_border_score=Decimal(str(scores["border"])),
                abcde_color="uniform" if scores["color"] == 0 else "varied",
                abcde_color_score=Decimal(str(scores["color"])),
                abcde_diameter_mm=Decimal("4.5") if scores["diameter"] == 0 else Decimal("7.2"),
                abcde_diameter_score=Decimal(str(scores["diameter"])),
                abcde_evolving="stable" if scores["evolving"] == 0 else "changing",
                abcde_evolving_score=Decimal(str(scores["evolving"])),
                abcde_total_score=Decimal(str(total_score)),
                abcde_risk_level=lesion_data["risk"],
                length_mm=Decimal("5.2"),
                width_mm=Decimal("4.8"),
                malignancy_risk=lesion_data["risk"],
                biopsy_recommended=total_score >= 4,
                biopsy_urgency="routine" if total_score < 6 else "urgent" if total_score < 8 else "emergent",
                photography_performed=True,
                dermoscopy_performed=True,
                dermoscopy_features={"network": True, "globules": False, "streaks": lesion_data["risk"] == "high"}
            )
            db.add(lesion)


def create_pediatrics_sample_data(db: Session, patients):
    """Create sample pediatrics data"""
    
    pediatric_patients = [p for p in patients if p["specialty"] == "pediatrics"]
    
    for patient_data in pediatric_patients:
        fhir_patient = patient_data["fhir_patient"]
        patient = patient_data["patient"]
        
        # Calculate age in days and months
        birth_date = patient.birth_date
        today = date.today()
        age_days = (today - birth_date).days
        age_months = age_days / 30.44  # Average days per month
        
        # Create growth chart data
        for i in range(5):  # 5 measurements over time
            measurement_date = birth_date + timedelta(days=int(age_days * (i + 1) / 6))
            measurement_age_days = (measurement_date - birth_date).days
            measurement_age_months = measurement_age_days / 30.44
            
            # Create FHIR Observation for growth
            fhir_observation = FHIRObservation(
                patient_id=fhir_patient.id,
                status="final",
                category=[{"coding": [{"code": "vital-signs", "system": "http://terminology.hl7.org/CodeSystem/observation-category"}]}],
                code={"coding": [{"code": "9843-4", "system": "http://loinc.org", "display": "Head Occipital-frontal circumference"}]},
                subject=f"Patient/{fhir_patient.patient_id}",
                effective_datetime=datetime.combine(measurement_date, datetime.min.time()),
                specialty_data={"specialty": "pediatrics", "measurement_type": "growth"}
            )
            db.add(fhir_observation)
            db.flush()
            
            # Realistic growth data based on age
            if measurement_age_months < 6:
                weight = 3.5 + (measurement_age_months * 0.7)  # kg
                height = 50 + (measurement_age_months * 2.5)   # cm
                head_circ = 35 + (measurement_age_months * 0.8)  # cm
            elif measurement_age_months < 12:
                weight = 7.5 + ((measurement_age_months - 6) * 0.4)
                height = 65 + ((measurement_age_months - 6) * 1.5)
                head_circ = 40 + ((measurement_age_months - 6) * 0.4)
            else:
                weight = 10 + ((measurement_age_months - 12) * 0.25)
                height = 75 + ((measurement_age_months - 12) * 1.0)
                head_circ = 45 + ((measurement_age_months - 12) * 0.2)
            
            # Calculate BMI and percentiles (simplified)
            bmi = weight / ((height / 100) ** 2)
            weight_percentile = min(95, max(5, 50 + (weight - 10) * 5))
            height_percentile = min(95, max(5, 50 + (height - 75) * 2))
            
            growth_chart = PediatricsGrowthChart(
                fhir_observation_id=fhir_observation.id,
                measurement_date=measurement_date,
                age_at_measurement_days=Decimal(str(measurement_age_days)),
                age_at_measurement_months=Decimal(str(round(measurement_age_months, 2))),
                weight_kg=Decimal(str(round(weight, 2))),
                weight_percentile=Decimal(str(round(weight_percentile, 1))),
                height_cm=Decimal(str(round(height, 1))),
                height_percentile=Decimal(str(round(height_percentile, 1))),
                head_circumference_cm=Decimal(str(round(head_circ, 1))),
                head_circumference_percentile=Decimal("50.0"),
                bmi=Decimal(str(round(bmi, 2))),
                bmi_percentile=Decimal("50.0"),
                chart_type="WHO",
                nutritional_status="normal",
                feeding_method="breastfeeding" if measurement_age_months < 6 else "mixed"
            )
            db.add(growth_chart)
        
        # Create vaccination records
        vaccines = [
            {"name": "Hepatitis B", "age_days": 1, "dose": 1},
            {"name": "BCG", "age_days": 7, "dose": 1},
            {"name": "Hepatitis B", "age_days": 60, "dose": 2},
            {"name": "DTP", "age_days": 60, "dose": 1},
            {"name": "Hib", "age_days": 60, "dose": 1},
            {"name": "Polio", "age_days": 60, "dose": 1},
            {"name": "Pneumococcal", "age_days": 60, "dose": 1},
        ]
        
        for vaccine in vaccines:
            admin_date = birth_date + timedelta(days=vaccine["age_days"])
            if admin_date <= today:  # Only past vaccinations
                # Create FHIR Procedure for vaccination
                from app.models.fhir_base import FHIRProcedure
                fhir_procedure = FHIRProcedure(
                    patient_id=fhir_patient.id,
                    status="completed",
                    category={"coding": [{"code": "vaccination", "system": "http://terminology.hl7.org/CodeSystem/procedure-category"}]},
                    code={"coding": [{"code": "33879002", "system": "http://snomed.info/sct", "display": "Administration of vaccine"}]},
                    subject=f"Patient/{fhir_patient.patient_id}",
                    performed_datetime=datetime.combine(admin_date, datetime.min.time()),
                    specialty_data={"specialty": "pediatrics", "vaccine_name": vaccine["name"]}
                )
                db.add(fhir_procedure)
                db.flush()
                
                vaccination = PediatricsVaccination(
                    fhir_procedure_id=fhir_procedure.id,
                    vaccine_name=vaccine["name"],
                    administration_date=admin_date,
                    dose_number=Decimal(str(vaccine["dose"])),
                    age_at_administration_days=Decimal(str(vaccine["age_days"])),
                    age_at_administration_months=Decimal(str(round(vaccine["age_days"] / 30.44, 2))),
                    administration_site="left_thigh",
                    administration_route="IM",
                    schedule_compliance="on_time",
                    catch_up_vaccine=False,
                    adverse_events_reported=False,
                    series_complete=vaccine["dose"] >= 3  # Simplified logic
                )
                db.add(vaccination)


def main():
    """Main function to create sample data"""
    print("Creating sample data for multi-specialty EHR system...")
    
    # Create tables (this should be done via Alembic in production)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create sample patients
        print("Creating sample patients...")
        patients = create_sample_patients(db)
        
        # Create dermatology data
        print("Creating dermatology sample data...")
        create_dermatology_sample_data(db, patients)
        
        # Create pediatrics data
        print("Creating pediatrics sample data...")
        create_pediatrics_sample_data(db, patients)
        
        db.commit()
        print(f"Successfully created sample data for {len(patients)} patients!")
        
        # Print summary
        dermatology_count = len([p for p in patients if p["specialty"] == "dermatology"])
        pediatrics_count = len([p for p in patients if p["specialty"] == "pediatrics"])
        
        print(f"\nSample data summary:")
        print(f"- {dermatology_count} dermatology patients with examinations and lesions")
        print(f"- {pediatrics_count} pediatric patients with growth charts and vaccinations")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()