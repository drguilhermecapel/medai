"""
Tests for API endpoints to ensure complete coverage.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock, patch
import json
from datetime import datetime

from app.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test_token"}

class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_detailed_health_check(self, client):
        """Test detailed health check."""
        response = client.get("/health/detailed")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "database" in data
        assert "redis" in data
        assert "ml_models" in data

    def test_readiness_check(self, client):
        """Test readiness check."""
        response = client.get("/ready")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ready"] is True

class TestECGEndpoints:
    """Test ECG analysis endpoints."""

    def test_upload_ecg(self, client, auth_headers):
        """Test ECG file upload."""
        # Mock file upload
        files = {"file": ("test_ecg.xml", b"<ecg>test data</ecg>", "application/xml")}
        data = {"patient_id": "123"}
        
        with patch('app.api.endpoints.ecg.ECGService') as mock_service:
            mock_service.return_value.create_analysis.return_value = {"id": 1}
            
            response = client.post(
                "/api/v1/ecg/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert "id" in result

    def test_get_ecg_analysis(self, client, auth_headers):
        """Test getting ECG analysis results."""
        analysis_id = 123
        
        with patch('app.api.endpoints.ecg.ECGService') as mock_service:
            mock_service.return_value.get_analysis.return_value = {
                "id": analysis_id,
                "status": "completed",
                "diagnosis": "Normal Sinus Rhythm",
                "confidence": 0.95
            }
            
            response = client.get(
                f"/api/v1/ecg/analysis/{analysis_id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["id"] == analysis_id
            assert result["diagnosis"] == "Normal Sinus Rhythm"

    def test_list_ecg_analyses(self, client, auth_headers):
        """Test listing ECG analyses."""
        with patch('app.api.endpoints.ecg.ECGService') as mock_service:
            mock_service.return_value.list_analyses.return_value = {
                "items": [
                    {"id": 1, "status": "completed"},
                    {"id": 2, "status": "processing"}
                ],
                "total": 2,
                "page": 1,
                "pages": 1
            }
            
            response = client.get(
                "/api/v1/ecg/analyses",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert len(result["items"]) == 2
            assert result["total"] == 2

    def test_download_ecg_report(self, client, auth_headers):
        """Test downloading ECG report."""
        analysis_id = 123
        
        with patch('app.api.endpoints.ecg.ECGService') as mock_service:
            mock_service.return_value.generate_report.return_value = b"PDF content"
            
            response = client.get(
                f"/api/v1/ecg/analysis/{analysis_id}/report",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "application/pdf"

    def test_real_time_ecg_stream(self, client, auth_headers):
        """Test real-time ECG streaming endpoint."""
        # This would typically use WebSocket
        with patch('app.api.endpoints.ecg.ECGService') as mock_service:
            mock_service.return_value.process_stream.return_value = {
                "heart_rate": 75,
                "rhythm": "normal"
            }
            
            response = client.post(
                "/api/v1/ecg/stream",
                json={"data": [0.1, 0.2, 0.3]},
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK

class TestPatientEndpoints:
    """Test patient management endpoints."""

    def test_create_patient(self, client, auth_headers):
        """Test patient creation."""
        patient_data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "medical_record_number": "MRN123456"
        }
        
        with patch('app.api.endpoints.patient.PatientService') as mock_service:
            mock_service.return_value.create_patient.return_value = {
                "id": 1,
                **patient_data
            }
            
            response = client.post(
                "/api/v1/patients",
                json=patient_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert result["first_name"] == "John"
            assert "id" in result

    def test_get_patient(self, client, auth_headers):
        """Test getting patient details."""
        patient_id = 123
        
        with patch('app.api.endpoints.patient.PatientService') as mock_service:
            mock_service.return_value.get_patient.return_value = {
                "id": patient_id,
                "first_name": "John",
                "last_name": "Doe",
                "medical_history": []
            }
            
            response = client.get(
                f"/api/v1/patients/{patient_id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["id"] == patient_id

    def test_update_patient(self, client, auth_headers):
        """Test updating patient information."""
        patient_id = 123
        update_data = {"phone": "+1234567890"}
        
        with patch('app.api.endpoints.patient.PatientService') as mock_service:
            mock_service.return_value.update_patient.return_value = {
                "id": patient_id,
                "phone": "+1234567890"
            }
            
            response = client.patch(
                f"/api/v1/patients/{patient_id}",
                json=update_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["phone"] == "+1234567890"

    def test_search_patients(self, client, auth_headers):
        """Test patient search."""
        with patch('app.api.endpoints.patient.PatientService') as mock_service:
            mock_service.return_value.search_patients.return_value = {
                "items": [
                    {"id": 1, "name": "John Doe"},
                    {"id": 2, "name": "Jane Doe"}
                ],
                "total": 2
            }
            
            response = client.get(
                "/api/v1/patients/search?q=Doe",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert len(result["items"]) == 2

class TestValidationEndpoints:
    """Test medical validation endpoints."""

    def test_create_validation(self, client, auth_headers):
        """Test creating validation request."""
        validation_data = {
            "analysis_id": 123,
            "notes": "Please review this ECG"
        }
        
        with patch('app.api.endpoints.validation.ValidationService') as mock_service:
            mock_service.return_value.create_validation.return_value = {
                "id": 1,
                "status": "pending",
                **validation_data
            }
            
            response = client.post(
                "/api/v1/validations",
                json=validation_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert result["status"] == "pending"

    def test_submit_validation(self, client, auth_headers):
        """Test submitting validation results."""
        validation_id = 123
        validation_result = {
            "status": "approved",
            "diagnosis_confirmed": True,
            "physician_notes": "Diagnosis confirmed"
        }
        
        with patch('app.api.endpoints.validation.ValidationService') as mock_service:
            mock_service.return_value.submit_validation.return_value = {
                "id": validation_id,
                **validation_result
            }
            
            response = client.put(
                f"/api/v1/validations/{validation_id}",
                json=validation_result,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["status"] == "approved"

    def test_get_pending_validations(self, client, auth_headers):
        """Test getting pending validations."""
        with patch('app.api.endpoints.validation.ValidationService') as mock_service:
            mock_service.return_value.get_pending_validations.return_value = [
                {"id": 1, "status": "pending", "priority": "high"},
                {"id": 2, "status": "pending", "priority": "medium"}
            ]
            
            response = client.get(
                "/api/v1/validations/pending",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert len(result) == 2

class TestStatisticsEndpoints:
    """Test statistics and analytics endpoints."""

    def test_get_dashboard_stats(self, client, auth_headers):
        """Test dashboard statistics."""
        with patch('app.api.endpoints.statistics.StatisticsService') as mock_service:
            mock_service.return_value.get_dashboard_stats.return_value = {
                "total_analyses": 1000,
                "analyses_today": 50,
                "average_processing_time": 2.5,
                "accuracy_rate": 0.95
            }
            
            response = client.get(
                "/api/v1/statistics/dashboard",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["total_analyses"] == 1000
            assert result["accuracy_rate"] == 0.95

    def test_get_performance_metrics(self, client, auth_headers):
        """Test performance metrics endpoint."""
        with patch('app.api.endpoints.statistics.StatisticsService') as mock_service:
            mock_service.return_value.get_performance_metrics.return_value = {
                "ml_model_performance": {
                    "sensitivity": 0.98,
                    "specificity": 0.97,
                    "f1_score": 0.96
                },
                "processing_times": {
                    "p50": 1.5,
                    "p95": 3.2,
                    "p99": 5.0
                }
            }
            
            response = client.get(
                "/api/v1/statistics/performance",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["ml_model_performance"]["sensitivity"] == 0.98

    def test_export_statistics(self, client, auth_headers):
        """Test statistics export."""
        with patch('app.api.endpoints.statistics.StatisticsService') as mock_service:
            mock_service.return_value.export_statistics.return_value = b"CSV data"
            
            response = client.get(
                "/api/v1/statistics/export?format=csv",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "text/csv"

class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_login(self, client):
        """Test user login."""
        login_data = {
            "username": "test@example.com",
            "password": "test_password"
        }
        
        with patch('app.api.endpoints.auth.AuthService') as mock_service:
            mock_service.return_value.authenticate.return_value = {
                "access_token": "test_token",
                "token_type": "bearer",
                "expires_in": 3600
            }
            
            response = client.post(
                "/api/v1/auth/login",
                data=login_data
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert "access_token" in result
            assert result["token_type"] == "bearer"

    def test_refresh_token(self, client):
        """Test token refresh."""
        with patch('app.api.endpoints.auth.AuthService') as mock_service:
            mock_service.return_value.refresh_token.return_value = {
                "access_token": "new_token",
                "token_type": "bearer"
            }
            
            response = client.post(
                "/api/v1/auth/refresh",
                headers={"Authorization": "Bearer old_token"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["access_token"] == "new_token"

    def test_logout(self, client, auth_headers):
        """Test user logout."""
        with patch('app.api.endpoints.auth.AuthService') as mock_service:
            mock_service.return_value.logout.return_value = True
            
            response = client.post(
                "/api/v1/auth/logout",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["message"] == "Successfully logged out"

class TestWebSocketEndpoints:
    """Test WebSocket endpoints."""

    @pytest.mark.asyncio
    async def test_ecg_websocket(self, client):
        """Test ECG real-time WebSocket."""
        from fastapi.testclient import TestClient
        
        with client.websocket_connect("/ws/ecg/123") as websocket:
            # Send ECG data
            websocket.send_json({
                "type": "ecg_data",
                "data": [0.1, 0.2, 0.3, 0.4, 0.5]
            })
            
            # Receive analysis
            data = websocket.receive_json()
            assert data["type"] == "analysis"
            assert "heart_rate" in data

    @pytest.mark.asyncio
    async def test_notifications_websocket(self, client):
        """Test notifications WebSocket."""
        with client.websocket_connect("/ws/notifications") as websocket:
            # Simulate receiving notification
            websocket.send_json({
                "type": "subscribe",
                "channels": ["alerts", "updates"]
            })
            
            data = websocket.receive_json()
            assert data["type"] == "subscribed"

class TestErrorHandling:
    """Test API error handling."""

    def test_404_not_found(self, client):
        """Test 404 error handling."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        result = response.json()
        assert "detail" in result

    def test_401_unauthorized(self, client):
        """Test 401 unauthorized."""
        response = client.get("/api/v1/ecg/analyses")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_400_bad_request(self, client, auth_headers):
        """Test 400 bad request."""
        response = client.post(
            "/api/v1/patients",
            json={"invalid": "data"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_500_internal_error(self, client, auth_headers):
        """Test 500 internal server error handling."""
        with patch('app.api.endpoints.ecg.ECGService') as mock_service:
            mock_service.return_value.get_analysis.side_effect = Exception("Internal error")
            
            response = client.get(
                "/api/v1/ecg/analysis/123",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            result = response.json()
            assert "detail" in result

class TestRateLimiting:
    """Test API rate limiting."""

    def test_rate_limit_exceeded(self, client, auth_headers):
        """Test rate limit enforcement."""
        # Make multiple requests quickly
        for i in range(100):
            response = client.get("/api/v1/health", headers=auth_headers)
            
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                result = response.json()
                assert "detail" in result
                assert "rate limit" in result["detail"].lower()
                break
        else:
            # If rate limiting is not configured, skip this test
            pytest.skip("Rate limiting not configured")

class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers(self, client):
        """Test CORS headers."""
        response = client.options(
            "/api/v1/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers