"""
Tests for Dermatology API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import uuid4

from app.main import app
from app.models.fhir_base import FHIRPatient, FHIRCondition
from app.models.specialties.dermatology import DermatologyLesion


class TestDermatologyAPI:
    """Test cases for Dermatology API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_patient(self, db: Session):
        """Create a sample FHIR patient for testing"""
        fhir_patient = FHIRPatient(
            patient_id=uuid4(),
            active=True,
            name=[{
                "use": "official",
                "family": "Test",
                "given": ["Patient"]
            }],
            gender="female",
            birth_date="1985-01-01"
        )
        db.add(fhir_patient)
        db.commit()
        db.refresh(fhir_patient)
        return fhir_patient
    
    def test_create_lesion(self, client: TestClient, sample_patient: FHIRPatient):
        """Test creating a new dermatological lesion"""
        lesion_data = {
            "patient_id": str(sample_patient.id),
            "lesion_type": "melanocytic_nevus",
            "anatomical_location": "left_shoulder",
            "body_region": "trunk",
            "abcde_asymmetry": "symmetric",
            "abcde_asymmetry_score": 0,
            "abcde_border": "regular", 
            "abcde_border_score": 0,
            "abcde_color": "uniform",
            "abcde_color_score": 0,
            "abcde_diameter_mm": 4.5,
            "abcde_diameter_score": 0,
            "abcde_evolving": "stable",
            "abcde_evolving_score": 0,
            "length_mm": 5.0,
            "width_mm": 4.5,
            "photography_performed": True,
            "dermoscopy_performed": True
        }
        
        response = client.post("/api/v1/specialties/dermatology/lesions", json=lesion_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["lesion_type"] == "melanocytic_nevus"
        assert data["anatomical_location"] == "left_shoulder"
        assert data["abcde_total_score"] == 0.0
        assert data["abcde_risk_level"] == "low"
        assert data["biopsy_recommended"] is False
    
    def test_create_high_risk_lesion(self, client: TestClient, sample_patient: FHIRPatient):
        """Test creating a high-risk lesion that triggers biopsy recommendation"""
        lesion_data = {
            "patient_id": str(sample_patient.id),
            "lesion_type": "suspicious_lesion",
            "anatomical_location": "forehead",
            "body_region": "head",
            "abcde_asymmetry": "asymmetric",
            "abcde_asymmetry_score": 2,
            "abcde_border": "irregular",
            "abcde_border_score": 2,
            "abcde_color": "varied",
            "abcde_color_score": 2,
            "abcde_diameter_mm": 8.0,
            "abcde_diameter_score": 2,
            "abcde_evolving": "changing",
            "abcde_evolving_score": 2,
            "length_mm": 8.5,
            "width_mm": 7.8,
            "photography_performed": True,
            "dermoscopy_performed": True
        }
        
        response = client.post("/api/v1/specialties/dermatology/lesions", json=lesion_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["lesion_type"] == "suspicious_lesion"
        assert data["abcde_total_score"] == 10.0
        assert data["abcde_risk_level"] == "critical"
        assert data["biopsy_recommended"] is True
        assert data["biopsy_urgency"] == "emergent"
        assert data["needs_urgent_referral"] is True
    
    def test_list_lesions(self, client: TestClient, sample_patient: FHIRPatient, db: Session):
        """Test listing lesions with filtering"""
        # Create a sample lesion first
        fhir_condition = FHIRCondition(
            patient_id=sample_patient.id,
            clinical_status={"coding": [{"code": "active"}]},
            code={"coding": [{"code": "400006008", "display": "Skin lesion"}]},
            subject=f"Patient/{sample_patient.patient_id}"
        )
        db.add(fhir_condition)
        db.flush()
        
        lesion = DermatologyLesion(
            fhir_condition_id=fhir_condition.id,
            lesion_type="melanocytic_nevus",
            anatomical_location="left_shoulder",
            body_region="trunk",
            abcde_total_score=Decimal("2.0"),
            abcde_risk_level="low"
        )
        db.add(lesion)
        db.commit()
        
        # Test listing all lesions
        response = client.get("/api/v1/specialties/dermatology/lesions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Test filtering by patient ID
        response = client.get(f"/api/v1/specialties/dermatology/lesions?patient_id={sample_patient.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(lesion["anatomical_location"] for lesion in data)
    
    def test_get_lesion(self, client: TestClient, sample_patient: FHIRPatient, db: Session):
        """Test getting a specific lesion"""
        # Create a sample lesion
        fhir_condition = FHIRCondition(
            patient_id=sample_patient.id,
            clinical_status={"coding": [{"code": "active"}]},
            code={"coding": [{"code": "400006008", "display": "Skin lesion"}]},
            subject=f"Patient/{sample_patient.patient_id}"
        )
        db.add(fhir_condition)
        db.flush()
        
        lesion = DermatologyLesion(
            fhir_condition_id=fhir_condition.id,
            lesion_type="atypical_nevus",
            anatomical_location="right_calf",
            body_region="leg"
        )
        db.add(lesion)
        db.commit()
        
        # Test getting the lesion
        response = client.get(f"/api/v1/specialties/dermatology/lesions/{fhir_condition.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["lesion_type"] == "atypical_nevus"
        assert data["anatomical_location"] == "right_calf"
    
    def test_get_nonexistent_lesion(self, client: TestClient):
        """Test getting a non-existent lesion returns 404"""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/specialties/dermatology/lesions/{fake_id}")
        assert response.status_code == 404
    
    def test_update_lesion(self, client: TestClient, sample_patient: FHIRPatient, db: Session):
        """Test updating a lesion"""
        # Create a sample lesion
        fhir_condition = FHIRCondition(
            patient_id=sample_patient.id,
            clinical_status={"coding": [{"code": "active"}]},
            code={"coding": [{"code": "400006008", "display": "Skin lesion"}]},
            subject=f"Patient/{sample_patient.patient_id}"
        )
        db.add(fhir_condition)
        db.flush()
        
        lesion = DermatologyLesion(
            fhir_condition_id=fhir_condition.id,
            lesion_type="melanocytic_nevus",
            anatomical_location="left_shoulder",
            abcde_asymmetry_score=Decimal("0"),
            abcde_border_score=Decimal("0"),
            abcde_color_score=Decimal("0"),
            abcde_diameter_score=Decimal("0"),
            abcde_evolving_score=Decimal("0")
        )
        db.add(lesion)
        db.commit()
        
        # Test updating the lesion
        update_data = {
            "abcde_asymmetry": "asymmetric",
            "abcde_asymmetry_score": 1,
            "clinical_suspicion": "atypical nevus",
            "follow_up_interval_months": 6
        }
        
        response = client.put(f"/api/v1/specialties/dermatology/lesions/{fhir_condition.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["abcde_asymmetry"] == "asymmetric"
        assert data["clinical_suspicion"] == "atypical nevus"
        assert data["abcde_total_score"] == 1.0  # Should be recalculated
    
    def test_perform_abcde_assessment(self, client: TestClient, sample_patient: FHIRPatient, db: Session):
        """Test performing ABCDE assessment"""
        # Create a sample lesion
        fhir_condition = FHIRCondition(
            patient_id=sample_patient.id,
            clinical_status={"coding": [{"code": "active"}]},
            code={"coding": [{"code": "400006008", "display": "Skin lesion"}]},
            subject=f"Patient/{sample_patient.patient_id}"
        )
        db.add(fhir_condition)
        db.flush()
        
        lesion = DermatologyLesion(
            fhir_condition_id=fhir_condition.id,
            lesion_type="suspicious_lesion",
            anatomical_location="back"
        )
        db.add(lesion)
        db.commit()
        
        # Perform ABCDE assessment
        abcde_data = {
            "asymmetry": "asymmetric",
            "asymmetry_score": 2,
            "border": "irregular",
            "border_score": 2,
            "color": "varied",
            "color_score": 1,
            "diameter_mm": 7.5,
            "diameter_score": 1,
            "evolving": "changing",
            "evolving_score": 2
        }
        
        response = client.post(f"/api/v1/specialties/dermatology/lesions/{fhir_condition.id}/abcde", json=abcde_data)
        assert response.status_code == 200
        data = response.json()
        assert data["abcde_total_score"] == 8.0
        assert data["risk_level"] == "critical"
        assert data["biopsy_recommended"] is True
        assert data["biopsy_urgency"] == "emergent"
        assert data["malignancy_risk"] == "very_high"
    
    def test_create_examination(self, client: TestClient, sample_patient: FHIRPatient):
        """Test creating a dermatology examination"""
        examination_data = {
            "patient_id": str(sample_patient.id),
            "examination_type": "full_body",
            "examination_scope": ["head", "neck", "trunk", "arms", "legs"],
            "fitzpatrick_skin_type": "III",
            "sunscreen_use": "regular",
            "family_history_skin_cancer": False,
            "total_moles_count": 30,
            "atypical_moles_count": 3,
            "overall_skin_condition": "good",
            "risk_stratification": "low",
            "recommendations": ["Annual skin check", "Daily sunscreen"],
            "next_examination_interval": 12
        }
        
        response = client.post("/api/v1/specialties/dermatology/examinations", json=examination_data)
        assert response.status_code == 201
        data = response.json()
        assert data["examination_type"] == "full_body"
        assert data["fitzpatrick_skin_type"] == "III"
        assert data["total_moles_count"] == 30
        assert data["risk_stratification"] == "low"
    
    def test_get_lesion_statistics(self, client: TestClient, sample_patient: FHIRPatient, db: Session):
        """Test getting lesion statistics"""
        # Create sample lesions with different risk levels
        for i, risk_level in enumerate(["low", "moderate", "high"]):
            fhir_condition = FHIRCondition(
                patient_id=sample_patient.id,
                clinical_status={"coding": [{"code": "active"}]},
                code={"coding": [{"code": "400006008", "display": "Skin lesion"}]},
                subject=f"Patient/{sample_patient.patient_id}"
            )
            db.add(fhir_condition)
            db.flush()
            
            lesion = DermatologyLesion(
                fhir_condition_id=fhir_condition.id,
                lesion_type=f"lesion_{i}",
                anatomical_location=f"location_{i}",
                body_region="trunk",
                abcde_risk_level=risk_level,
                biopsy_recommended=risk_level != "low",
                biopsy_urgency="urgent" if risk_level == "high" else "routine"
            )
            db.add(lesion)
        
        db.commit()
        
        # Test getting statistics
        response = client.get("/api/v1/specialties/dermatology/statistics/lesion-summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_lesions" in data
        assert "risk_distribution" in data
        assert "biopsies_recommended" in data
        assert "region_distribution" in data
        
        assert data["total_lesions"] >= 3
        assert data["risk_distribution"]["low"] >= 1
        assert data["risk_distribution"]["moderate"] >= 1  
        assert data["risk_distribution"]["high"] >= 1
        assert data["biopsies_recommended"] >= 2  # moderate and high risk
    
    def test_validation_error_missing_required_fields(self, client: TestClient):
        """Test validation error when required fields are missing"""
        incomplete_data = {
            "lesion_type": "melanocytic_nevus"
            # Missing patient_id and anatomical_location
        }
        
        response = client.post("/api/v1/specialties/dermatology/lesions", json=incomplete_data)
        assert response.status_code == 422  # Validation error
    
    def test_validation_error_invalid_scores(self, client: TestClient, sample_patient: FHIRPatient):
        """Test validation error for invalid ABCDE scores"""
        invalid_data = {
            "patient_id": str(sample_patient.id),
            "lesion_type": "melanocytic_nevus",
            "anatomical_location": "left_shoulder",
            "abcde_asymmetry_score": 3.0  # Invalid: should be 0-2
        }
        
        response = client.post("/api/v1/specialties/dermatology/lesions", json=invalid_data)
        assert response.status_code == 422  # Validation error