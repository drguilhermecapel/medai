# find_missing_imports.py
import os
import re
import ast

def find_imports_from_constants(filepath):
    """Encontra todos os imports de app.core.constants em um arquivo"""
    imports = set()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse do AST para encontrar imports
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'app.core.constants':
                    for alias in node.names:
                        imports.add(alias.name)
    except:
        # Fallback para regex se AST falhar
        pattern = re.compile(r'from\s+app\.core\.constants\s+import\s+([^(\n]+)')
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = pattern.findall(content)
        for match in matches:
            items = [item.strip() for item in match.split(',')]
            imports.update(items)
    
    return imports

# Coletar todos os imports
all_imports = set()

for root, dirs, files in os.walk('app'):
    if '__pycache__' in root:
        continue
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            imports = find_imports_from_constants(filepath)
            if imports:
                all_imports.update(imports)
                print(f"{filepath}: {', '.join(sorted(imports))}")

print(f"\n\nTodos os imports únicos de app.core.constants:")
for imp in sorted(all_imports):
    print(f"  - {imp}")

# Verificar o que já existe em constants.py
print("\n\nVerificando o que já existe em constants.py...")
constants_file = os.path.join('app', 'core', 'constants.py')
if os.path.exists(constants_file):
    with open(constants_file, 'r', encoding='utf-8') as f:
        constants_content = f.read()
    
    print("\nImports que parecem estar FALTANDO:")
    for imp in sorted(all_imports):
        if imp not in constants_content:
            print(f"  - {imp}")
else:
    print("Arquivo constants.py não encontrado!")