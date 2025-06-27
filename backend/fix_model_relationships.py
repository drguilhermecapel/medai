#!/usr/bin/env python3
"""
Script para corrigir os relacionamentos nos modelos
"""
import os
import re

# Lista de arquivos para corrigir
model_files = [
    "app/models/ecg_analysis.py",
    "app/models/ecg_record.py"
]

def fix_ecg_analysis():
    """Corrige o modelo ECGAnalysis"""
    file_path = "app/models/ecg_analysis.py"
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adiciona import se não existir
        if "from app.models.patient import Patient" not in content:
            # Adiciona após os outros imports
            import_section = re.search(r'(from app\.database import.*?\n)', content)
            if import_section:
                insert_pos = import_section.end()
                content = content[:insert_pos] + "from app.models.patient import Patient\n" + content[insert_pos:]
        
        # Salva
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path} corrigido")
    else:
        print(f"❌ {file_path} não encontrado")

def fix_ecg_record():
    """Corrige o modelo ECGRecord"""
    file_path = "app/models/ecg_record.py"
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adiciona import se não existir
        if "from app.models.user import User" not in content:
            # Adiciona após os outros imports
            import_section = re.search(r'(from app\.database import.*?\n)', content)
            if import_section:
                insert_pos = import_section.end()
                content = content[:insert_pos] + "from app.models.user import User\n" + content[insert_pos:]
        
        # Salva
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path} corrigido")
    else:
        print(f"❌ {file_path} não encontrado")

if __name__ == "__main__":
    print("🔧 Corrigindo relacionamentos nos modelos...")
    fix_ecg_analysis()
    fix_ecg_record()
    print("\n✅ Correções aplicadas!")