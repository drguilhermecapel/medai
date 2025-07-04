import ast
from pathlib import Path

def fix_syntax_file(file_path):
    """Tenta corrigir erros de sintaxe básicos"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se é um erro de sintaxe simples
        try:
            ast.parse(content)
            print(f"✅ {file_path} - Sintaxe OK")
            return True
        except SyntaxError as e:
            print(f"🔧 {file_path} - Erro linha {e.lineno}: {e.msg}")
            
            # Tentativas de correção automática
            lines = content.split('\n')
            
            # Erro de chave não fechada
            if 'unmatched' in str(e.msg):
                # Tentar adicionar chave faltante
                if e.lineno <= len(lines):
                    error_line = lines[e.lineno - 1]
                    if error_line.strip() == '}':
                        # Remover chave extra
                        lines[e.lineno - 1] = ''
                    elif not error_line.strip().endswith(('}', ')', ']')):
                        # Adicionar chave/parêntese faltante baseado no contexto
                        lines[e.lineno - 1] = error_line + '}'
                
                fixed_content = '\n'.join(lines)
                
                # Verificar se correção funcionou
                try:
                    ast.parse(fixed_content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    print(f"✅ {file_path} - Sintaxe corrigida automaticamente")
                    return True
                except:
                    print(f"❌ {file_path} - Correção automática falhou")
                    return False
            
            return False
            
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

# Arquivos com erros de sintaxe
syntax_error_files = [
    'tests/test_integration_comprehensive.py',
    'tests/test_ml_model_service_enhanced.py'
]

for file_path in syntax_error_files:
    if Path(file_path).exists():
        fix_syntax_file(file_path)

print("✅ Erros de sintaxe processados")

