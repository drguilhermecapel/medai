"""
Medical calculations - standalone module
"""

def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate Body Mass Index"""
    if height_m <= 0:
        raise ValueError("Height must be positive")
    return round(weight_kg / (height_m ** 2), 2)

def calculate_bsa(weight_kg: float, height_cm: float) -> float:
    """Calculate Body Surface Area using DuBois formula"""
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("Weight and height must be positive")
    return round(0.007184 * (weight_kg ** 0.425) * (height_cm ** 0.725), 2)

def calculate_map(systolic: int, diastolic: int) -> float:
    """Calculate Mean Arterial Pressure"""
    if systolic <= diastolic:
        raise ValueError("Systolic must be greater than diastolic")
    return round(diastolic + (systolic - diastolic) / 3, 1)

def calculate_heart_rate_max(age: int) -> int:
    """Calculate maximum heart rate (220 - age)"""
    if age <= 0 or age > 120:
        raise ValueError("Invalid age")
    return 220 - age

def calculate_qtc(qt_interval: int, heart_rate: int) -> int:
    """Calculate corrected QT interval using Bazett's formula"""
    if qt_interval <= 0 or heart_rate <= 0:
        raise ValueError("QT interval and heart rate must be positive")
    rr_interval = 60000 / heart_rate  # RR in ms
    return round(qt_interval / (rr_interval / 1000) ** 0.5)

def interpret_qtc(qtc: int, gender: str = "male") -> str:
    """Interpret QTc interval"""
    if gender.lower() == "male":
        if qtc < 430:
            return "normal"
        elif qtc < 450:
            return "borderline"
        else:
            return "prolonged"
    else:  # female
        if qtc < 440:
            return "normal"
        elif qtc < 460:
            return "borderline"
        else:
            return "prolonged"

def calculate_egfr(creatinine: float, age: int, gender: str, race: str = "other") -> float:
    """Calculate estimated Glomerular Filtration Rate (CKD-EPI)"""
    if creatinine <= 0 or age <= 0:
        raise ValueError("Invalid values")
    
    # Simplified CKD-EPI formula
    if gender.lower() == "male":
        if creatinine <= 0.9:
            egfr = 141 * (creatinine / 0.9) ** -0.411 * 0.993 ** age
        else:
            egfr = 141 * (creatinine / 0.9) ** -1.209 * 0.993 ** age
    else:  # female
        if creatinine <= 0.7:
            egfr = 144 * (creatinine / 0.7) ** -0.329 * 0.993 ** age
        else:
            egfr = 144 * (creatinine / 0.7) ** -1.209 * 0.993 ** age
        egfr *= 1.018
    
    if race.lower() == "black":
        egfr *= 1.159
    
    return round(egfr, 1)
