import re
from pathlib import Path

def fix_duplicate_tables():
    """Corrige problema de tabelas duplicadas no SQLAlchemy"""
    
    # Encontrar arquivos de modelo
    model_files = list(Path('app/models').glob('*.py'))
    
    for model_file in model_files:
        if model_file.name == '__init__.py':
            continue
            
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar extend_existing=True às tabelas
        if '__tablename__' in content and 'extend_existing' not in content:
            # Encontrar definições de tabela e adicionar extend_existing
            pattern = r'(__tablename__\s*=\s*[\'"][^\'"]+[\'"])'
            replacement = r'\1\n    __table_args__ = {"extend_existing": True}'
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                
                with open(model_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Corrigido: {model_file}")

fix_duplicate_tables()
print("✅ Problema de tabelas duplicadas corrigido")

