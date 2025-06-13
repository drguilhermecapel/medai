# test_specific_lines_coverage.py
"""
Specific tests targeting uncovered lines identified in the coverage report
"""

from datetime import timedelta
from unittest.mock import Mock, patch

import numpy as np
import pytest
from fastapi import HTTPException


# Target auth.py uncovered lines (32, 39, 71-88, 96-110, 122)
class TestAuthEndpointCoverage:
    """Test uncovered lines in auth endpoints"""

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, db_session):
        """Cover lines 71-88 - invalid login handling"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client, db_session):
        """Cover lines 96-110 - inactive user login"""
        # Create inactive user
        from app.core.security import get_password_hash
        from app.models.user import User

        inactive_user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password=get_password_hash("password"),
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()

        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "password"
            }
        )
        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client):
        """Cover line 122 - invalid refresh token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


# Target config.py uncovered lines (47-58, 69-77, 92-100, 111-114, 124, 127, 168, 172, 181, 185)
class TestConfigCoverage:
    """Test uncovered configuration lines"""

    def test_settings_validation_errors(self):
        """Cover validation error handling in config"""
        from app.core.config import Settings

        # Test with invalid values
        with pytest.raises(ValueError):
            Settings(
                POSTGRES_SERVER="",  # Empty server
                POSTGRES_DB="",
                SECRET_KEY="short"  # Too short
            )

    def test_settings_computed_properties(self):
        """Cover computed properties"""
        from app.core.config import Settings

        settings = Settings()

        # Test SQLALCHEMY_DATABASE_URI construction
        assert settings.SQLALCHEMY_DATABASE_URI.startswith("postgresql://")

        # Test CORS origins parsing
        assert isinstance(settings.BACKEND_CORS_ORIGINS, list)

        # Test email configuration
        if settings.EMAILS_ENABLED:
            assert settings.EMAILS_FROM_EMAIL is not None

    def test_celery_config_generation(self):
        """Cover Celery configuration generation"""
        from app.core.config import Settings

        settings = Settings()
        celery_config = settings.get_celery_config()

        assert "broker_url" in celery_config
        assert "result_backend" in celery_config
        assert celery_config["task_serializer"] == "json"


# Target security.py uncovered lines (47-55, 65, 82-92, 96-108, 112, 116, 120, 124-125, 131-133, 137, 148)
class TestSecurityCoverage:
    """Test uncovered security functions"""

    def test_create_access_token_with_expires(self):
        """Cover custom expiration in create_access_token"""
        from app.core.security import create_access_token

        data = {"sub": "test@example.com"}
        custom_expires = timedelta(hours=2)

        token = create_access_token(data, expires_delta=custom_expires)
        assert token is not None
        assert isinstance(token, str)

    def test_verify_token_expired(self):
        """Cover expired token verification"""
        from app.core.security import create_access_token, verify_token

        # Create token that expires immediately
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        # Verify should fail
        payload = verify_token(token)
        assert payload is None

    def test_verify_token_invalid(self):
        """Cover invalid token verification"""
        from app.core.security import verify_token

        invalid_tokens = [
            "not.a.token",
            "invalid_jwt_format",
            "",
            None
        ]

        for token in invalid_tokens:
            assert verify_token(token) is None

    def test_get_current_user_no_token(self):
        """Cover missing token in get_current_user"""
        from app.core.security import get_current_user

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=None, db=Mock())

        assert exc_info.value.status_code == 401

    def test_get_current_user_invalid_payload(self):
        """Cover invalid payload in token"""
        from app.core.security import create_access_token, get_current_user

        # Create token without 'sub' field
        token = create_access_token({"invalid": "payload"})

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=Mock())

        assert exc_info.value.status_code == 401


# Target ecg_analysis.py uncovered lines (50-56, 89, 124, 227-228, 254-255, 288, 297-323, 336)
class TestECGAnalysisEndpointCoverage:
    """Test uncovered ECG analysis endpoint lines"""

    @pytest.mark.asyncio
    async def test_upload_ecg_invalid_format(self, client, authorized_headers):
        """Cover lines 50-56 - invalid file format"""
        # Upload non-ECG file
        files = {"file": ("test.txt", b"not an ecg file", "text/plain")}

        response = await client.post(
            "/api/v1/ecg/upload",
            files=files,
            headers=authorized_headers
        )
        assert response.status_code == 400
        assert "format" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_analysis_not_found(self, client, authorized_headers):
        """Cover line 89 - analysis not found"""
        response = await client.get(
            "/api/v1/ecg/analysis/nonexistent_id",
            headers=authorized_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_analysis_not_found(self, client, authorized_headers):
        """Cover line 124 - delete non-existent analysis"""
        response = await client.delete(
            "/api/v1/ecg/analysis/nonexistent_id",
            headers=authorized_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_validate_analysis_errors(self, client, authorized_headers):
        """Cover lines 227-228, 254-255 - validation errors"""
        # Invalid analysis ID
        response = await client.post(
            "/api/v1/ecg/analysis/invalid_id/validate",
            json={"validation_result": "approved"},
            headers=authorized_headers
        )
        assert response.status_code == 404

        # Invalid validation data
        response = await client.post(
            "/api/v1/ecg/analysis/some_id/validate",
            json={"invalid": "data"},
            headers=authorized_headers
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_export_batch_empty(self, client, authorized_headers):
        """Cover lines 297-323 - empty batch export"""
        response = await client.post(
            "/api/v1/ecg/export/batch",
            json={"analysis_ids": []},
            headers=authorized_headers
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_reprocess_analysis_failure(self, client, authorized_headers):
        """Cover line 336 - reprocessing failure"""
        with patch('app.api.v1.endpoints.ecg_analysis.ecg_service.reprocess_analysis') as mock_reprocess:
            mock_reprocess.side_effect = Exception("Processing failed")

            response = await client.post(
                "/api/v1/ecg/analysis/some_id/reprocess",
                headers=authorized_headers
            )
            assert response.status_code == 500


# Target user repository uncovered lines (64-70)
class TestUserRepositoryCoverage:
    """Test uncovered user repository lines"""

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, db_session):
        """Cover lines 64-70 - update non-existent user"""
        from app.repositories.user_repository import UserRepository

        repo = UserRepository(db_session)
        result = await repo.update_user(
            user_id="nonexistent_id",
            update_data={"email": "new@example.com"}
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, db_session):
        """Cover user deletion when not found"""
        from app.repositories.user_repository import UserRepository

        repo = UserRepository(db_session)
        result = await repo.delete_user("nonexistent_id")
        assert result is False


# Target validation repository uncovered lines
class TestValidationRepositoryCoverage:
    """Test uncovered validation repository lines"""

    @pytest.mark.asyncio
    async def test_get_pending_validations_empty(self, db_session):
        """Cover empty pending validations"""
        from app.repositories.validation_repository import ValidationRepository

        repo = ValidationRepository(db_session)
        pending = await repo.get_pending_validations(limit=10)
        assert pending == []

    @pytest.mark.asyncio
    async def test_get_validations_by_validator(self, db_session):
        """Cover getting validations by validator"""
        from app.repositories.validation_repository import ValidationRepository

        repo = ValidationRepository(db_session)
        validations = await repo.get_validations_by_validator(
            validator_id="validator123",
            status="completed"
        )
        assert isinstance(validations, list)

    @pytest.mark.asyncio
    async def test_bulk_update_validations(self, db_session):
        """Cover bulk update operations"""
        from app.models.validation import ECGValidation
        from app.repositories.validation_repository import ValidationRepository

        # Create test validations
        validations = [
            ECGValidation(
                analysis_id=f"analysis_{i}",
                requested_by="user123",
                priority="normal"
            )
            for i in range(3)
        ]

        for v in validations:
            db_session.add(v)
        db_session.commit()

        repo = ValidationRepository(db_session)
        validation_ids = [v.validation_id for v in validations]

        # Bulk update
        updated = await repo.bulk_update_validations(
            validation_ids=validation_ids,
            update_data={"status": "in_progress"}
        )
        assert updated == len(validation_ids)


# Target preprocessing advanced_pipeline.py uncovered lines
class TestAdvancedPipelineCoverage:
    """Test uncovered advanced pipeline preprocessing"""

    def test_pipeline_edge_cases(self):
        """Cover edge cases in preprocessing pipeline"""
        from app.preprocessing.advanced_pipeline import AdvancedECGPreprocessor

        preprocessor = AdvancedECGPreprocessor()

        # Test with extremely noisy signal
        noisy_signal = np.random.randn(12, 5000) * 10
        processed = preprocessor.preprocess(noisy_signal)
        assert processed.shape == noisy_signal.shape

        # Test with flat line (no signal)
        flat_signal = np.zeros((12, 5000))
        processed = preprocessor.preprocess(flat_signal)
        assert not np.isnan(processed).any()

        # Test with clipped signal
        clipped_signal = np.random.randn(12, 5000)
        clipped_signal[clipped_signal > 1] = 1
        clipped_signal[clipped_signal < -1] = -1
        processed = preprocessor.preprocess(clipped_signal)
        assert processed.shape == clipped_signal.shape

    def test_adaptive_filtering(self):
        """Test adaptive filtering methods"""
        from app.preprocessing.advanced_pipeline import AdvancedECGPreprocessor

        preprocessor = AdvancedECGPreprocessor()

        # Test with baseline wander
        t = np.linspace(0, 10, 5000)
        baseline_wander = 0.5 * np.sin(2 * np.pi * 0.1 * t)
        signal = np.random.randn(12, 5000) + baseline_wander

        filtered = preprocessor.remove_baseline_wander(signal)

        # Baseline should be reduced
        assert np.std(filtered.mean(axis=1)) < np.std(signal.mean(axis=1))

    def test_artifact_detection(self):
        """Test artifact detection and removal"""
        from app.preprocessing.advanced_pipeline import AdvancedECGPreprocessor

        preprocessor = AdvancedECGPreprocessor()

        # Create signal with artifacts
        signal = np.random.randn(12, 5000)
        # Add motion artifact
        signal[:, 1000:1500] += np.random.randn(12, 500) * 5

        artifacts = preprocessor.detect_artifacts(signal)
        assert len(artifacts) > 0
        assert any(1000 <= start <= 1500 for start, end in artifacts)


# Target enhanced quality analyzer uncovered lines
class TestEnhancedQualityAnalyzerCoverage:
    """Test uncovered quality analyzer lines"""

    def test_quality_metrics_edge_cases(self):
        """Test quality metrics with edge cases"""
        from app.preprocessing.enhanced_quality_analyzer import EnhancedQualityAnalyzer

        analyzer = EnhancedQualityAnalyzer()

        # Test with perfect signal
        perfect_signal = np.sin(2 * np.pi * np.linspace(0, 10, 5000))
        quality = analyzer.analyze_signal_quality(perfect_signal)
        assert quality['overall_score'] > 0.9

        # Test with pure noise
        noise_signal = np.random.randn(5000) * 10
        quality = analyzer.analyze_signal_quality(noise_signal)
        assert quality['overall_score'] < 0.3

        # Test with NaN values
        nan_signal = np.random.randn(5000)
        nan_signal[100:200] = np.nan
        quality = analyzer.analyze_signal_quality(nan_signal)
        assert quality['has_missing_data']

    def test_lead_quality_assessment(self):
        """Test individual lead quality assessment"""
        from app.preprocessing.enhanced_quality_analyzer import EnhancedQualityAnalyzer

        analyzer = EnhancedQualityAnalyzer()

        # Create 12-lead with varying quality
        signal = np.random.randn(12, 5000)
        # Make lead V1 very noisy
        signal[6] *= 10
        # Make lead V2 flat
        signal[7] = 0

        lead_qualities = analyzer.assess_lead_quality(signal)

        assert lead_qualities[6] < 0.5  # V1 should have low quality
        assert lead_qualities[7] < 0.1  # V2 should have very low quality

    def test_automatic_quality_improvement(self):
        """Test automatic quality improvement suggestions"""
        from app.preprocessing.enhanced_quality_analyzer import EnhancedQualityAnalyzer

        analyzer = EnhancedQualityAnalyzer()

        # Signal with specific issues
        signal = np.random.randn(12, 5000)

        # Add 60Hz noise
        t = np.linspace(0, 10, 5000)
        signal += 0.5 * np.sin(2 * np.pi * 60 * t)

        suggestions = analyzer.suggest_improvements(signal)
        assert any('60 Hz' in s or 'powerline' in s.lower() for s in suggestions)


# Target ML model service uncovered lines
class TestMLModelServiceCoverage:
    """Test uncovered ML model service lines"""

    @pytest.mark.asyncio
    async def test_model_loading_errors(self):
        """Test model loading error handling"""
        from app.services.ml_model_service import MLModelService

        with patch('app.services.ml_model_service.load_model') as mock_load:
            mock_load.side_effect = Exception("Model file corrupted")

            service = MLModelService()
            # Should handle error gracefully
            assert service.model is None or hasattr(service, 'fallback_mode')

    @pytest.mark.asyncio
    async def test_batch_inference_memory_limit(self):
        """Test batch inference with memory limits"""
        from app.services.ml_model_service import MLModelService

        service = MLModelService()

        # Large batch that might exceed memory
        large_batch = [np.random.randn(12, 5000) for _ in range(1000)]

        # Should process in chunks
        results = await service.batch_inference(large_batch, max_batch_size=100)
        assert len(results) == len(large_batch)

    def test_feature_extraction_fallback(self):
        """Test feature extraction fallback mechanisms"""
        from app.services.ml_model_service import MLModelService

        service = MLModelService()

        # Signal that might cause feature extraction issues
        problematic_signal = np.zeros((12, 5000))
        problematic_signal[0, :10] = [np.inf, -np.inf, np.nan] * 3 + [0]

        features = service.extract_features(problematic_signal)
        assert not np.isnan(features).any()
        assert not np.isinf(features).any()


# Target notification service uncovered lines
class TestNotificationServiceCoverage:
    """Test uncovered notification service lines"""

    @pytest.mark.asyncio
    async def test_send_email_notification_failure(self):
        """Test email notification failure handling"""
        from app.services.notification_service import NotificationService

        with patch('app.services.notification_service.send_email') as mock_send:
            mock_send.side_effect = Exception("SMTP error")

            service = NotificationService()
            result = await service.send_critical_finding_alert(
                user_email="test@example.com",
                finding="Critical ST elevation",
                analysis_id="12345"
            )

            # Should handle error and possibly try alternative notification
            assert not result['email_sent']
            assert 'error' in result

    @pytest.mark.asyncio
    async def test_batch_notifications(self):
        """Test batch notification sending"""
        from app.services.notification_service import NotificationService

        service = NotificationService()

        notifications = [
            {
                'user_id': f'user_{i}',
                'message': f'Test notification {i}',
                'type': 'info'
            }
            for i in range(50)
        ]

        results = await service.send_batch_notifications(notifications)
        assert len(results) == len(notifications)

    @pytest.mark.asyncio
    async def test_notification_preferences(self):
        """Test notification preference handling"""
        from app.services.notification_service import NotificationService

        service = NotificationService()

        # User with specific preferences
        user_preferences = {
            'email_enabled': False,
            'sms_enabled': True,
            'critical_only': True
        }

        # Non-critical notification should be filtered
        result = await service.send_notification(
            user_id="user123",
            message="Regular update",
            severity="info",
            user_preferences=user_preferences
        )

        assert not result['sent']
        assert result['reason'] == 'filtered_by_preferences'


# Target patient service uncovered lines
class TestPatientServiceCoverage:
    """Test uncovered patient service lines"""

    @pytest.mark.asyncio
    async def test_patient_merge(self):
        """Test patient record merging"""
        from app.services.patient_service import PatientService

        service = PatientService()

        # Merge duplicate patient records
        result = await service.merge_patient_records(
            primary_id="patient_001",
            duplicate_id="patient_002",
            merge_strategy="keep_latest"
        )

        assert result['success']
        assert result['merged_fields'] is not None

    @pytest.mark.asyncio
    async def test_patient_data_export(self):
        """Test patient data export functionality"""
        from app.services.patient_service import PatientService

        service = PatientService()

        # Export patient data for GDPR compliance
        export_data = await service.export_patient_data(
            patient_id="patient_123",
            format="json",
            include_analyses=True
        )

        assert 'patient_info' in export_data
        assert 'ecg_analyses' in export_data
        assert 'metadata' in export_data


# Target validation service uncovered lines
class TestValidationServiceCoverage:
    """Test uncovered validation service lines"""

    @pytest.mark.asyncio
    async def test_auto_validation_rules(self):
        """Test automatic validation rules"""
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Analysis that should trigger auto-validation
        analysis_result = {
            'diagnosis': 'Normal Sinus Rhythm',
            'confidence': 0.98,
            'quality_score': 0.95,
            'critical_findings': []
        }

        auto_validation = await service.apply_auto_validation_rules(analysis_result)
        assert auto_validation['can_auto_validate']
        assert auto_validation['reason'] == 'high_confidence_normal'

    @pytest.mark.asyncio
    async def test_validation_queue_management(self):
        """Test validation queue management"""
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Get queue statistics
        stats = await service.get_queue_statistics()
        assert 'pending_count' in stats
        assert 'average_wait_time' in stats
        assert 'validators_available' in stats

    @pytest.mark.asyncio
    async def test_consensus_validation(self):
        """Test consensus validation for critical cases"""
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Critical finding requiring multiple validators
        critical_analysis = {
            'analysis_id': 'critical_123',
            'findings': ['STEMI', 'Acute MI'],
            'confidence': 0.85
        }

        consensus_request = await service.request_consensus_validation(
            analysis=critical_analysis,
            num_validators=3,
            max_wait_time=3600  # 1 hour
        )

        assert consensus_request['status'] == 'pending'
        assert consensus_request['validators_needed'] == 3


# Integration test for full coverage boost
class TestIntegrationCoverage:
    """Integration tests to boost overall coverage"""

    @pytest.mark.asyncio
    async def test_complete_ecg_workflow(self, client, authorized_headers, db_session):
        """Test complete ECG analysis workflow"""
        # 1. Upload ECG
        ecg_data = self._generate_test_ecg_file()
        files = {"file": ("test_ecg.xml", ecg_data, "application/xml")}

        upload_response = await client.post(
            "/api/v1/ecg/upload",
            files=files,
            headers=authorized_headers
        )
        assert upload_response.status_code == 200
        analysis_id = upload_response.json()["analysis_id"]

        # 2. Wait for processing
        import asyncio
        await asyncio.sleep(2)

        # 3. Get analysis result
        analysis_response = await client.get(
            f"/api/v1/ecg/analysis/{analysis_id}",
            headers=authorized_headers
        )
        assert analysis_response.status_code == 200

        # 4. Request validation
        validation_response = await client.post(
            f"/api/v1/ecg/analysis/{analysis_id}/request-validation",
            json={"priority": "high", "notes": "Please verify ST changes"},
            headers=authorized_headers
        )
        assert validation_response.status_code == 200

        # 5. Generate report
        report_response = await client.get(
            f"/api/v1/ecg/analysis/{analysis_id}/report",
            headers=authorized_headers
        )
        assert report_response.status_code == 200
        assert report_response.headers["content-type"] == "application/pdf"

    def _generate_test_ecg_file(self):
        """Generate a test ECG file"""
        # Simplified ECG XML structure
        ecg_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <ECG>
            <Patient>
                <ID>TEST001</ID>
                <Name>Test Patient</Name>
                <Age>65</Age>
            </Patient>
            <Recording>
                <SampleRate>500</SampleRate>
                <Duration>10</Duration>
                <Leads>
                    <Lead name="I">{}</Lead>
                    <Lead name="II">{}</Lead>
                </Leads>
            </Recording>
        </ECG>
        """.format(
            ','.join(map(str, np.random.randn(5000).tolist())),
            ','.join(map(str, np.random.randn(5000).tolist()))
        )
        return ecg_xml.encode('utf-8')


# Memory and performance edge cases
class TestMemoryAndPerformance:
    """Test memory management and performance edge cases"""

    def test_memory_leak_prevention(self):
        """Test that there are no memory leaks in critical paths"""
        import gc
        import tracemalloc

        from app.services.advanced_ml_service import AdvancedMLService

        tracemalloc.start()
        initial_memory = tracemalloc.get_traced_memory()[0]

        service = AdvancedMLService()

        # Process many signals
        for i in range(100):
            signal = np.random.randn(12, 5000)
            _ = service.preprocess_signal(signal)

            if i % 20 == 0:
                gc.collect()

        gc.collect()
        final_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        # Memory increase should be minimal (< 50MB)
        memory_increase = (final_memory - initial_memory) / 1024 / 1024
        assert memory_increase < 50

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self):
        """Test handling of concurrent requests"""
        import asyncio

        from app.services.ecg_service import ECGService

        service = ECGService()

        # Create multiple concurrent requests
        tasks = []
        for i in range(20):
            signal = np.random.randn(12, 5000)
            task = service.create_analysis(
                signal_data=signal,
                patient_id=f"patient_{i}",
                metadata={}
            )
            tasks.append(task)

        # All should complete without errors
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check that most succeeded
        successes = sum(1 for r in results if not isinstance(r, Exception))
        assert successes >= 18  # Allow for some failures due to resource constraints


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=term-missing"])
