# fix_table_extend.py
import os
import re

def add_extend_existing(filepath):
    """Adiciona extend_existing a um modelo se necessário"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já tem __table_args__
    if '__table_args__' in content:
        print(f"✓ {filepath} já tem __table_args__")
        return False
    
    # Padrão para encontrar __tablename__
    pattern = re.compile(r'(\s+__tablename__\s*=\s*["\'][^"\']+["\'])')
    
    def replacement(match):
        return match.group(0) + '\n    __table_args__ = {\'extend_existing\': True}'
    
    new_content = pattern.sub(replacement, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Adicionado extend_existing a {filepath}")
        return True
    
    return False

# Processar todos os modelos
models_dir = os.path.join('app', 'models')
count = 0

for file in os.listdir(models_dir):
    if file.endswith('.py') and file not in ['__init__.py', 'base.py']:
        filepath = os.path.join(models_dir, file)
        if add_extend_existing(filepath):
            count += 1

print(f"\nTotal de arquivos modificados: {count}")