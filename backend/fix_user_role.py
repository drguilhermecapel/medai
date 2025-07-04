import re

# Ler arquivo constants
with open('app/core/constants.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar se VIEWER já existe
if 'VIEWER' not in content:
    # Encontrar enum UserRole e adicionar VIEWER
    if 'class UserRole' in content:
        # Adicionar VIEWER ao enum após PATIENT
        content = re.sub(
            r'(PATIENT = "patient")',
            r'\1\n    VIEWER = "viewer"',
            content
        )
        print("✅ VIEWER adicionado ao UserRole")
    else:
        # Criar enum completo se não existir
        user_role_enum = '''
class UserRole(str, Enum):
    """User roles enumeration"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    VIEWER = "viewer"
    PATIENT = "patient"
'''
        content += user_role_enum
        print("✅ UserRole enum criado com VIEWER")
    
    # Salvar arquivo
    with open('app/core/constants.py', 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("✅ VIEWER já existe no UserRole")

