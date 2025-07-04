import re

# Ler arquivo
with open('tests/test_ml_model_service_enhanced.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir ModelType. incompletos
content = re.sub(
    r'ml_service\.models = \{\s*ModelType\.\s*\}',
    'ml_service.models = {\n            # Mock models dictionary - empty for this test\n        }',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Salvar arquivo
with open('tests/test_ml_model_service_enhanced.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ ModelType incompletos corrigidos")

