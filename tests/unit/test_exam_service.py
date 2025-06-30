import pytest
from app.services.exam_service import ExamService

def test_create_exam():
    service = ExamService()
    result = service.create_exam({"type": "blood"})
    assert "id" in result

def test_process_results():
    service = ExamService()
    result = service.process_exam_results(1, {"glucose": 95})
    assert result["processed"]

def test_validate_exam():
    service = ExamService()
    assert service.validate_exam_data({"type": "blood"})

def test_exam_history():
    service = ExamService()
    history = service.get_exam_history(1)
    assert isinstance(history, list)
