#!/usr/bin/env python3
"""
Script completo para resolver todos os problemas de encoding e executar testes
"""

import subprocess
import sys
import os
from pathlib import Path


def install_dependencies():
    """Instala dependências necessárias"""
    print("📦 Instalando dependências necessárias...")
    
    dependencies = [
        'chardet',  # Para detecção de encoding
        'pytest',
        'pytest-cov',
        'pytest-asyncio'
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=True, capture_output=True)
            print(f"   ✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"   ❌ Falha ao instalar {dep}")


def run_encoding_fix():
    """Executa a correção de encoding"""
    print("\n🔧 Executando correção de encoding...")
    
    # Primeiro, tentar a correção rápida
    try:
        exec(open('quick_fix_encoding.py').read())
        print("   ✅ Correção rápida executada")
    except Exception as e:
        print(f"   ❌ Erro na correção rápida: {e}")
        
        # Se falhar, tentar a correção completa
        try:
            exec(open('fix_encoding_issues.py').read())
            print("   ✅ Correção completa executada")
        except Exception as e:
            print(f"   ❌ Erro na correção completa: {e}")


def test_import_files():
    """Testa se os arquivos podem ser importados sem erro de encoding"""
    print("\n🧪 Testando importação dos arquivos...")
    
    files_to_test = [
        'app.config',
        'app.security', 
        'app.services.ml_model_service',
        'app.services.validation_service'
    ]
    
    all_ok = True
    
    for module_name in files_to_test:
        try:
            # Tentar importar o módulo
            __import__(module_name)
            print(f"   ✅ {module_name}: importação OK")
        except UnicodeDecodeError as e:
            print(f"   ❌ {module_name}: erro de encoding - {e}")
            all_ok = False
        except ImportError as e:
            print(f"   ⚠️  {module_name}: erro de importação - {e}")
        except SyntaxError as e:
            if 'utf-8' in str(e).lower():
                print(f"   ❌ {module_name}: erro de encoding - {e}")
                all_ok = False
            else:
                print(f"   ⚠️  {module_name}: erro de sintaxe - {e}")
        except Exception as e:
            print(f"   ❌ {module_name}: erro inesperado - {e}")
    
    return all_ok


def run_pytest():
    """Executa os testes com pytest"""
    print("\n🧪 Executando testes...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/unit/', '-v', 
            '--cov=app', 
            '--cov-report=term-missing',
            '--tb=short'
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("   ✅ Testes executados com sucesso!")
        else:
            print(f"   ❌ Testes falharam (código de saída: {result.returncode})")
            
            # Verificar se ainda há erros de encoding
            if 'utf-8' in result.stdout.lower() or 'utf-8' in result.stderr.lower():
                print("   ⚠️  Ainda há problemas de encoding")
                return False
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"   ❌ Erro ao executar pytest: {e}")
        return False


def manual_encoding_fix():
    """Correção manual de encoding quando scripts automáticos falham"""
    print("\n🔧 Executando correção manual de encoding...")
    
    problematic_files = [
        'app/config.py',
        'app/services/ml_model_service.py',
        'app/security.py', 
        'app/services/validation_service.py'
    ]
    
    for file_path_str in problematic_files:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"   ❌ Arquivo não encontrado: {file_path}")
            continue
        
        print(f"   🔧 Corrigindo {file_path}...")
        
        try:
            # Tentar ler com Windows-1252 (encoding comum em Windows)
            with open(file_path, 'r', encoding='windows-1252') as f:
                content = f.read()
            
            # Salvar como UTF-8
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"      ✅ Convertido de windows-1252 para UTF-8")
            
        except Exception as e1:
            try:
                # Tentar com latin-1
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"      ✅ Convertido de latin-1 para UTF-8")
                
            except Exception as e2:
                print(f"      ❌ Falha na conversão: {e1}, {e2}")


def create_utf8_headers():
    """Adiciona headers UTF-8 aos arquivos Python"""
    print("\n📝 Adicionando headers UTF-8...")
    
    files = [
        'app/config.py',
        'app/services/ml_model_service.py',
        'app/security.py',
        'app/services/validation_service.py'
    ]
    
    for file_path_str in files:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Verificar se já tem header
            has_header = any('coding:' in line or 'encoding:' in line for line in lines[:3])
            
            if not has_header:
                print(f"   📝 Adicionando header a {file_path}")
                
                # Adicionar header
                if lines and lines[0].startswith('#!'):
                    lines.insert(1, '# -*- coding: utf-8 -*-\n')
                else:
                    lines.insert(0, '# -*- coding: utf-8 -*-\n')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
        
        except Exception as e:
            print(f"   ❌ Erro ao processar {file_path}: {e}")


def main():
    """Função principal do processo completo"""
    print("🚀 CORREÇÃO COMPLETA DE PROBLEMAS DE ENCODING")
    print("=" * 60)
    print()
    
    # 1. Instalar dependências
    install_dependencies()
    
    # 2. Tentar correção automática de encoding
    run_encoding_fix()
    
    # 3. Tentar correção manual se necessário
    manual_encoding_fix()
    
    # 4. Adicionar headers UTF-8
    create_utf8_headers()
    
    # 5. Testar importações
    print("\n" + "=" * 60)
    if test_import_files():
        print("   ✅ Todos os arquivos podem ser importados!")
    else:
        print("   ❌ Alguns arquivos ainda têm problemas")
    
    # 6. Executar testes
    print("\n" + "=" * 60)
    if run_pytest():
        print("\n🎉 SUCESSO! Testes executados sem erros de encoding!")
    else:
        print("\n⚠️  Ainda há problemas. Verifique os logs acima.")
        
        # Instruções adicionais
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Verifique se todos os arquivos estão salvos em UTF-8")
        print("2. Configure seu editor para usar UTF-8 por padrão")
        print("3. No VS Code: File → Preferences → Settings → Search 'encoding' → Set 'utf8'")
        print("4. Execute manualmente: python -c 'import app.config' para testar")


if __name__ == "__main__":
    main()