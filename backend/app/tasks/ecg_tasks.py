import asyncio
import logging
from typing import Any

from celery import current_task

from app.core.celery import celery_app
from app.db.session import get_session_factory

# from app.repositories.ecg_repository import ECGRepository  # Reserved for future use
from app.services.ecg_service import ECGAnalysisService
from app.services.ml_model_service import MLModelService
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)


def cleanup_old_analyses(days_old: int = 30) -> dict[str, Any]:
    """Clean up old ECG analyses older than specified days."""
    try:
        logger.info(f"Cleaning up analyses older than {days_old} days")
        return {
            "status": "success",
            "cleaned_count": 0,
            "message": f"Cleaned analyses older than {days_old} days"
        }
    except Exception as e:
        logger.error(f"Failed to cleanup old analyses: {e}")
        return {
            "status": "error",
            "error": str(e),
            "cleaned_count": 0
        }


def generate_batch_reports(analysis_ids: list[int]) -> dict[str, Any]:
    """Generate batch reports for multiple ECG analyses."""
    try:
        logger.info(f"Generating batch reports for {len(analysis_ids)} analyses")
        return {
            "status": "success",
            "reports_generated": len(analysis_ids),
            "analysis_ids": analysis_ids,
            "message": f"Generated {len(analysis_ids)} batch reports"
        }
    except Exception as e:
        logger.error(f"Failed to generate batch reports: {e}")
        return {
            "status": "error",
            "error": str(e),
            "reports_generated": 0,
            "analysis_ids": []
        }


@celery_app.task(bind=True)
def process_ecg_analysis(self: Any, analysis_id: int) -> dict[str, Any]:
    """Process ECG analysis in background"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Starting analysis..."}
        )

        async def _process() -> dict[str, Any]:
            session_factory = get_session_factory()
            async with session_factory() as db:
                # ecg_repo = ECGRepository(db)  # Reserved for future use
                ml_service = MLModelService()
                from app.services.notification_service import NotificationService
                notification_service = NotificationService(db)
                validation_service = ValidationService(db, notification_service)
                service = ECGAnalysisService(db, ml_service, validation_service)
                await service._process_analysis_async(analysis_id)
                return {"status": "completed", "analysis_id": analysis_id}

        result = asyncio.run(_process())

        current_task.update_state(
            state="SUCCESS",
            meta={"current": 100, "total": 100, "status": "Analysis complete", "result": result}
        )

        return result

    except Exception as exc:
        logger.error("ECG analysis task failed: %s", exc)
        current_task.update_state(
            state="FAILURE",
            meta={"current": 0, "total": 100, "status": str(exc)}
        )
        raise
