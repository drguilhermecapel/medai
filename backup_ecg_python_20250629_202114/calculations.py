"""
Simple utility functions without dependencies
"""

def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def subtract(a: int, b: int) -> int:
    """Subtract b from a"""
    return a - b

def is_even(n: int) -> bool:
    """Check if number is even"""
    return n % 2 == 0

def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI (weight in kg, height in meters)"""
    if height <= 0:
        raise ValueError("Height must be positive")
    return weight / (height ** 2)

def classify_bmi(bmi: float) -> str:
    """Classify BMI value"""
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"
