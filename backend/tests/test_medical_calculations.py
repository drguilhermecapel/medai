"""
Tests for medical calculations
"""
import pytest
from app.standalone.medical_calculations import (
    calculate_bmi, calculate_bsa, calculate_map,
    calculate_heart_rate_max, calculate_qtc, interpret_qtc,
    calculate_egfr
)

class TestMedicalCalculations:
    """Test medical calculation functions"""
    
    def test_calculate_bmi(self):
        # Normal cases
        assert calculate_bmi(70, 1.75) == 22.86
        assert calculate_bmi(80, 1.80) == 24.69
        assert calculate_bmi(55, 1.60) == 21.48
        
        # Edge cases
        with pytest.raises(ValueError):
            calculate_bmi(70, 0)
        with pytest.raises(ValueError):
            calculate_bmi(70, -1)
    
    def test_calculate_bsa(self):
        # Normal cases
        assert calculate_bsa(70, 175) == 1.85
        assert calculate_bsa(80, 180) == 2.00
        
        # Edge cases
        with pytest.raises(ValueError):
            calculate_bsa(0, 175)
        with pytest.raises(ValueError):
            calculate_bsa(70, -175)
    
    def test_calculate_map(self):
        # Normal blood pressure
        assert calculate_map(120, 80) == 93.3
        assert calculate_map(140, 90) == 106.7
        
        # Edge cases
        with pytest.raises(ValueError):
            calculate_map(80, 120)  # Systolic < Diastolic
    
    def test_calculate_heart_rate_max(self):
        assert calculate_heart_rate_max(20) == 200
        assert calculate_heart_rate_max(40) == 180
        assert calculate_heart_rate_max(60) == 160
        
        # Edge cases
        with pytest.raises(ValueError):
            calculate_heart_rate_max(0)
        with pytest.raises(ValueError):
            calculate_heart_rate_max(150)
    
    def test_calculate_qtc(self):
        # Normal heart rate (60 bpm, RR = 1000ms)
        assert calculate_qtc(400, 60) == 400
        
        # Tachycardia (120 bpm, RR = 500ms)
        assert calculate_qtc(350, 120) == 495
        
        # Edge cases
        with pytest.raises(ValueError):
            calculate_qtc(0, 60)
        with pytest.raises(ValueError):
            calculate_qtc(400, 0)
    
    def test_interpret_qtc(self):
        # Male
        assert interpret_qtc(420, "male") == "normal"
        assert interpret_qtc(440, "male") == "borderline"
        assert interpret_qtc(460, "male") == "prolonged"
        
        # Female
        assert interpret_qtc(430, "female") == "normal"
        assert interpret_qtc(450, "female") == "borderline"
        assert interpret_qtc(470, "female") == "prolonged"
    
    def test_calculate_egfr(self):
        # Normal kidney function
        egfr = calculate_egfr(1.0, 40, "male")
        assert 85 < egfr < 95  # Should be around 90
        
        # Female adjustment
        egfr_female = calculate_egfr(1.0, 40, "female")
        assert egfr_female > egfr  # Female has higher eGFR
        
        # Race adjustment
        egfr_black = calculate_egfr(1.0, 40, "male", "black")
        assert egfr_black > egfr  # Black race has higher eGFR
        
        # Edge cases
        with pytest.raises(ValueError):
            calculate_egfr(0, 40, "male")
        with pytest.raises(ValueError):
            calculate_egfr(1.0, 0, "male")
