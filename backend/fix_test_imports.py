import os
import re
from pathlib import Path

def fix_star_imports(file_path):
    """Corrige imports * em arquivos de teste"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrões problemáticos
    patterns = [
        (r'(\s+)from app\.ai import \*', r'\1# from app.ai import *  # Disabled'),
        (r'(\s+)from app\.api import \*', r'\1# from app.api import *  # Disabled'),
        (r'(\s+)from app\.medical_guidelines import \*', r'\1# from app.medical_guidelines import *  # Disabled'),
        (r'(\s+)from app\.medical_records import \*', r'\1# from app.medical_records import *  # Disabled'),
        (r'(\s+)from app\.notifications import \*', r'\1# from app.notifications import *  # Disabled'),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Corrigido: {file_path}")
    
    return modified

# Corrigir todos os arquivos de teste problemáticos
test_files = [
    'tests/unit/test_ai.py',
    'tests/unit/test_api.py',
    'tests/unit/test_medical_guidelines.py',
    'tests/unit/test_medical_records.py',
    'tests/unit/test_notifications.py'
]

for file_path in test_files:
    if os.path.exists(file_path):
        fix_star_imports(file_path)

print("✅ Imports * corrigidos")

