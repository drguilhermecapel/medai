"""Patient service."""
class PatientService:
    def __init__(self):
        self.db = None
    
    def create_patient(self, data: dict) -> dict:
        return {"id": 1, **data}
    
    def get_patient(self, patient_id: int) -> dict:
        return {"id": patient_id, "name": "Test Patient"}
    
    def update_patient(self, patient_id: int, data: dict) -> dict:
        return {"id": patient_id, **data}
    
    def delete_patient(self, patient_id: int) -> bool:
        return True
    
    def list_patients(self, filters: dict = None) -> list:
        return [{"id": 1, "name": "Patient 1"}]
