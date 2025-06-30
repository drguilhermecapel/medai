#!/usr/bin/env python3
"""
Setup completo de testes em um único comando.
Este script executa TUDO que é necessário para atingir >80% de cobertura.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Cores
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def run_command(cmd, description):
    """Executa um comando e mostra o resultado."""
    print(f"\n{Colors.BLUE}▶ {description}...{Colors.END}")
    
    if isinstance(cmd, str):
        # Se for string, executa como script Python
        exec(open(cmd).read())
        return True
    else:
        # Se for lista, executa como subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ {description} - Sucesso!{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ {description} - Falhou!{Colors.END}")
            if result.stderr:
                print(result.stderr)
            return False

def main():
    print(f"""
{Colors.BOLD}{Colors.BLUE}╔════════════════════════════════════════════════════════════╗
║        SETUP COMPLETO DE TESTES MEDAI - ALL IN ONE        ║
╚════════════════════════════════════════════════════════════╝{Colors.END}

Este script irá:
1. Corrigir imports e estrutura
2. Criar TODOS os arquivos de teste
3. Executar os testes com cobertura
4. Gerar relatório HTML

{Colors.YELLOW}⏱️  Tempo estimado: 2-3 minutos{Colors.END}
""")
    
    input("Pressione ENTER para começar...")
    
    start_time = time.time()
    
    # 1. Primeiro, cria o script fix_imports.py se não existir
    if not Path("fix_imports.py").exists():
        print(f"{Colors.BLUE}Criando fix_imports.py...{Colors.END}")
        with open("fix_imports.py", "w") as f:
            f.write('''import os
from pathlib import Path

def fix_app_init():
    app_init = Path("app/__init__.py")
    app_init.parent.mkdir(exist_ok=True)
    content = \'\'\'"""MedAI Application Package."""
__version__ = "1.0.0"
\'\'\'
    app_init.write_text(content)

def fix_services_init():
    services_init = Path("app/services/__init__.py")
    services_init.parent.mkdir(parents=True, exist_ok=True)
    services_init.write_text("")

def main():
    fix_app_init()
    fix_services_init()
    print("✅ Estrutura corrigida!")

if __name__ == "__main__":
    main()
''')
    
    # 2. Cria o script create_all_tests.py se não existir
    if not Path("create_all_tests.py").exists():
        print(f"{Colors.BLUE}Criando create_all_tests.py...{Colors.END}")
        # Aqui você deve copiar o conteúdo do artifact create_all_tests.py
        # Por brevidade, vou criar uma versão simplificada
        with open("create_all_tests.py", "w") as f:
            f.write('''print("Use o script create_all_tests.py do artifact anterior!")''')
        print(f"{Colors.YELLOW}⚠️  Por favor, copie o conteúdo de create_all_tests.py do artifact!{Colors.END}")
        return
    
    # 3. Executa os passos
    steps = [
        ([sys.executable, "fix_imports.py"], "Corrigindo imports e estrutura"),
        ([sys.executable, "create_all_tests.py"], "Criando arquivos de teste"),
        ([sys.executable, "-m", "pytest", "tests/", "-v", "--cov=app", 
          "--cov-report=html", "--cov-report=term"], "Executando testes com cobertura")
    ]
    
    all_success = True
    for cmd, description in steps:
        if not run_command(cmd, description):
            all_success = False
            print(f"\n{Colors.RED}Erro no passo: {description}{Colors.END}")
            break
        time.sleep(1)  # Pequena pausa entre passos
    
    # 4. Resultado final
    elapsed_time = time.time() - start_time
    
    if all_success:
        print(f"""
{Colors.GREEN}{Colors.BOLD}╔════════════════════════════════════════════════════════════╗
║                    ✅ SETUP COMPLETO!                      ║
╚════════════════════════════════════════════════════════════╝{Colors.END}

📊 Relatório de cobertura disponível em: {Colors.BLUE}htmlcov/index.html{Colors.END}
⏱️  Tempo total: {elapsed_time:.1f} segundos

{Colors.YELLOW}Abra o relatório HTML no navegador para ver a cobertura detalhada!{Colors.END}
""")
        
        # Tenta abrir o relatório automaticamente
        try:
            import webbrowser
            webbrowser.open(f"file://{Path('htmlcov/index.html').absolute()}")
            print(f"{Colors.GREEN}📄 Abrindo relatório no navegador...{Colors.END}")
        except:
            pass
    else:
        print(f"""
{Colors.RED}{Colors.BOLD}╔════════════════════════════════════════════════════════════╗
║                    ❌ SETUP FALHOU                         ║
╚════════════════════════════════════════════════════════════╝{Colors.END}

Por favor, verifique os erros acima e tente novamente.

Dicas:
1. Certifique-se de estar no diretório correto do projeto
2. Verifique se todas as dependências foram instaladas
3. Execute cada script individualmente para debug
""")

if __name__ == "__main__":
    main()