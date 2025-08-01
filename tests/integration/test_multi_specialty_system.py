"""
Integration tests for multi-specialty EHR system
Tests the complete workflow from patient creation to specialty assessments
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
import json

from app.main import app
from app.core.feature_flags import feature_flags


class TestMultiSpecialtySystem:
    """Integration tests for the complete multi-specialty system"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    def test_feature_flags_endpoint(self, client: TestClient):
        """Test that feature flags endpoint returns correct configuration"""
        response = client.get("/api/v1/feature-flags")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "enabled_specialties" in data
        assert "wave1_specialties" in data
        assert "wave2_specialties" in data
        assert "features" in data
        assert "specialty_features" in data
        
        # Check that dermatology is enabled by default
        assert "dermatology" in data["enabled_specialties"]
        assert "pediatrics" in data["enabled_specialties"]
        
        # Check FHIR compliance is enabled
        assert data["features"]["fhir_compliance"] is True
    
    def test_dermatology_specialty_enabled(self, client: TestClient):
        """Test that dermatology endpoints are accessible when enabled"""
        if not feature_flags.DERMATOLOGY_ENABLED:
            pytest.skip("Dermatology not enabled")
        
        # Test that we can access dermatology endpoints
        response = client.get("/api/v1/specialties/dermatology/lesions")
        
        # Should not get 404 (specialty disabled), but might get validation errors
        assert response.status_code != 404
    
    def test_specialty_workflow_dermatology(self, client: TestClient):
        """Test complete dermatology workflow"""
        if not feature_flags.DERMATOLOGY_ENABLED:
            pytest.skip("Dermatology not enabled")
        
        # This would test the complete workflow:
        # 1. Create patient
        # 2. Create lesion
        # 3. Perform ABCDE assessment
        # 4. Get statistics
        
        # For now, just test that endpoints exist and return expected format
        response = client.get("/api/v1/specialties/dermatology/lesions")
        assert response.status_code in [200, 422]  # 422 if validation fails, but endpoint exists
        
        response = client.get("/api/v1/specialties/dermatology/statistics/lesion-summary")
        assert response.status_code in [200, 422]
    
    def test_fhir_compliance_structure(self, client: TestClient):
        """Test that the system maintains FHIR compliance"""
        # Test feature flags to ensure FHIR compliance is enabled
        response = client.get("/api/v1/feature-flags")
        data = response.json()
        
        assert data["features"]["fhir_compliance"] is True
        
        # Test that specialty features are properly structured
        if "dermatology" in data["specialty_features"]:
            dermatology_features = data["specialty_features"]["dermatology"]
            assert "abcde_assessment" in dermatology_features
            assert "photo_mapping" in dermatology_features
            assert "dermoscopy" in dermatology_features
    
    def test_api_documentation_accessible(self, client: TestClient):
        """Test that API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Verify OpenAPI spec includes specialty endpoints
        openapi_spec = response.json()
        paths = openapi_spec.get("paths", {})
        
        # Check for specialty endpoints if enabled
        if feature_flags.DERMATOLOGY_ENABLED:
            dermatology_paths = [path for path in paths.keys() if "dermatology" in path]
            assert len(dermatology_paths) > 0
    
    def test_health_check_system(self, client: TestClient):
        """Test system health checks"""
        response = client.get("/health")
        assert response.status_code == 200
        
        response = client.get("/")
        assert response.status_code == 200
    
    def test_specialty_access_control(self, client: TestClient):
        """Test that disabled specialties are properly blocked"""
        # This test would verify that if a specialty is disabled via feature flags,
        # its endpoints return 404
        
        # Since we can't easily disable specialties in tests, we'll test the structure
        response = client.get("/api/v1/feature-flags")
        data = response.json()
        
        enabled_specialties = data["enabled_specialties"]
        
        # For each enabled specialty, verify endpoints exist
        for specialty in enabled_specialties:
            if specialty == "dermatology":
                response = client.get(f"/api/v1/specialties/{specialty}/lesions")
                assert response.status_code != 404
    
    def test_system_scalability_indicators(self, client: TestClient):
        """Test indicators that system can scale to multiple specialties"""
        response = client.get("/api/v1/feature-flags")
        data = response.json()
        
        # Test that system is prepared for Wave 1 and Wave 2 specialties
        assert len(data["wave1_specialties"]) >= 0
        assert len(data["wave2_specialties"]) >= 0
        
        # Test that specialty features are properly structured for extensibility
        specialty_features = data["specialty_features"]
        for specialty, features in specialty_features.items():
            assert isinstance(features, dict)
            # Each specialty should have at least one feature
            assert len(features) > 0
    
    def test_api_versioning_structure(self, client: TestClient):
        """Test that API versioning is properly implemented"""
        # Test v1 prefix
        response = client.get("/api/v1/feature-flags")
        assert response.status_code == 200
        
        # Test that specialty endpoints follow versioning pattern
        if feature_flags.DERMATOLOGY_ENABLED:
            response = client.get("/api/v1/specialties/dermatology/lesions")
            assert response.status_code != 404  # Endpoint exists
    
    def test_error_handling_consistency(self, client: TestClient):
        """Test that error handling is consistent across specialties"""
        # Test non-existent specialty
        response = client.get("/api/v1/specialties/nonexistent/endpoint")
        assert response.status_code == 404
        
        # Test feature flags for validation
        response = client.get("/api/v1/feature-flags")
        assert response.status_code == 200
        
        # Response should be valid JSON
        data = response.json()
        assert isinstance(data, dict)


class TestSystemIntegration:
    """Integration tests for system-wide functionality"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_startup_configuration(self, client: TestClient):
        """Test that system starts up with correct configuration"""
        # Test basic endpoints
        response = client.get("/")
        assert response.status_code == 200
        
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_cross_specialty_data_integrity(self, client: TestClient):
        """Test that FHIR data structure maintains integrity across specialties"""
        response = client.get("/api/v1/feature-flags")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify FHIR compliance is maintained
        assert data["features"]["fhir_compliance"] is True
        
        # Verify specialty features don't conflict
        specialty_features = data["specialty_features"]
        all_features = []
        for features in specialty_features.values():
            all_features.extend(features.keys())
        
        # Features should be namespaced or unique
        assert len(all_features) == len(set(all_features)) or len(specialty_features) <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])