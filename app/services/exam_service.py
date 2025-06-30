"""Exam service."""
class ExamService:
    def create_exam(self, data: dict) -> dict:
        return {"id": 1, **data}
    
    def process_exam_results(self, exam_id: int, results: dict) -> dict:
        return {"exam_id": exam_id, "processed": True}
    
    def validate_exam_data(self, data: dict) -> bool:
        return True
    
    def get_exam_history(self, patient_id: int) -> list:
        return [{"id": 1, "exam_type": "blood_test"}]
