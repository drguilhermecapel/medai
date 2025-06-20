from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ECGAnalysisBase(BaseModel):
    patient_id: int
    status: str
    clinical_urgency: str
    ai_diagnosis: str
    confidence_score: float

class ECGAnalysisCreate(ECGAnalysisBase):
    pass

class ECGAnalysis(ECGAnalysisBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


