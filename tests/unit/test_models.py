import pytest
from app.models import User, Patient, Exam, Diagnostic
from datetime import datetime

def test_user_model():
    user = User()
    user.email = "test@test.com"
    assert user.email == "test@test.com"

def test_patient_model():
    patient = Patient()
    patient.name = "Test Patient"
    assert patient.name == "Test Patient"

def test_exam_model():
    exam = Exam()
    exam.exam_type = "blood_test"
    assert exam.exam_type == "blood_test"

def test_diagnostic_model():
    diagnostic = Diagnostic()
    diagnostic.severity = "moderate"
    assert diagnostic.severity == "moderate"
