import re

# Ler arquivo
with open('tests/test_integration_comprehensive.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir imports incompletos
content = re.sub(
    r'from tests\.smart_mocks\s*$',
    'from tests.smart_mocks import SmartPatientMock, SmartECGMock',
    content,
    flags=re.MULTILINE
)

# Salvar arquivo
with open('tests/test_integration_comprehensive.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Imports incompletos corrigidos")

