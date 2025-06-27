"""
Standalone validators without dependencies
"""
import re

def validate_cpf(cpf: str) -> bool:
    """Validate Brazilian CPF"""
    if not cpf:
        return False
    
    # Remove non-digits
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    
    # Check length
    if len(cpf) != 11:
        return False
    
    # Check if all digits are the same
    if cpf == cpf[0] * 11:
        return False
    
    # Calculate first digit
    sum_digit = 0
    for i in range(9):
        sum_digit += int(cpf[i]) * (10 - i)
    
    first_digit = 11 - (sum_digit % 11)
    if first_digit >= 10:
        first_digit = 0
    
    if first_digit != int(cpf[9]):
        return False
    
    # Calculate second digit
    sum_digit = 0
    for i in range(10):
        sum_digit += int(cpf[i]) * (11 - i)
    
    second_digit = 11 - (sum_digit % 11)
    if second_digit >= 10:
        second_digit = 0
    
    return second_digit == int(cpf[10])

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate Brazilian phone number"""
    if not phone:
        return False
    
    # Remove non-digits
    phone = re.sub(r'[^0-9]', '', str(phone))
    
    # Check valid lengths (10 or 11 digits)
    return len(phone) in [10, 11]

def format_cpf(cpf: str) -> str:
    """Format CPF with dots and dash"""
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    
    if len(cpf) != 11:
        return cpf
    
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def format_phone(phone: str) -> str:
    """Format phone number"""
    phone = re.sub(r'[^0-9]', '', str(phone))
    
    if len(phone) == 11:
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    elif len(phone) == 10:
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
    else:
        return phone
