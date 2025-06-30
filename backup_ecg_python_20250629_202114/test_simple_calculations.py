"""
Tests for simple calculations
"""
import pytest
from app.utils.simple.calculations import add, subtract, is_even, calculate_bmi, classify_bmi

class TestCalculations:
    """Test calculation functions"""
    
    def test_add(self):
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0
    
    def test_subtract(self):
        assert subtract(5, 3) == 2
        assert subtract(0, 5) == -5
        assert subtract(-5, -3) == -2
    
    def test_is_even(self):
        assert is_even(2) == True
        assert is_even(3) == False
        assert is_even(0) == True
        assert is_even(-4) == True
    
    def test_calculate_bmi(self):
        # Normal case
        assert abs(calculate_bmi(70, 1.75) - 22.86) < 0.01
        
        # Edge cases
        with pytest.raises(ValueError):
            calculate_bmi(70, 0)
        
        with pytest.raises(ValueError):
            calculate_bmi(70, -1)
    
    def test_classify_bmi(self):
        assert classify_bmi(17.5) == "underweight"
        assert classify_bmi(22) == "normal"
        assert classify_bmi(27) == "overweight"
        assert classify_bmi(35) == "obese"
        
        # Edge cases
        assert classify_bmi(18.5) == "normal"
        assert classify_bmi(25) == "overweight"
        assert classify_bmi(30) == "obese"
