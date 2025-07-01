#!/usr/bin/env python3
"""
Correção rápida e específica para os arquivos com problemas de encoding
mencionados no erro do pytest
"""

import os
import shutil
from pathlib import Path


def create_backup(file_path):
    """Cria backup do arquivo"""
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
    shutil.copy2(file_path, backup_path)
    print(f"💾 Backup criado: {backup_path}")
    return backup_path


def fix_encoding_with_fallback(file_path):
    """Tenta corrigir encoding usando diferentes estratégias"""
    print(f"🔧 Corrigindo {file_path}...")
    
    # Criar backup
    create_backup(file_path)
    
    # Lista de encodings para tentar
    encodings_to_try = ['utf-8', 'windows-1252', 'latin-1', 'cp1252', 'iso-8859-1']
    
    content = None
    used_encoding = None
    
    # Tentar ler com diferentes encodings
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            print(f"   ✅ Lido com sucesso usando encoding: {encoding}")
            break
        except UnicodeDecodeError:
            print(f"   ❌ Falhou com encoding: {encoding}")
            continue
    
    if content is None:
        print(f"   ❌ Não foi possível ler o arquivo com nenhum encoding")
        return False
    
    # Salvar em UTF-8
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ Salvo como UTF-8")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao salvar como UTF-8: {e}")
        return False


def fix_specific_encoding_issues():
    """Corrige problemas específicos nos arquivos mencionados no pytest"""
    
    # Mapeamento de arquivos e correções específicas
    file_fixes = {
        'app/config.py': {
            'bad_chars': {
                'configura��o': 'configuração',
                'configura�ao': 'configuração',
                'configura\xe7\xe3o': 'configuração'
            }
        },
        'app/services/ml_model_service.py': {
            'bad_chars': {
                'cabe�a': 'cabeça',
                'cabe\xe7a': 'cabeça',
                'dor de cabe�a': 'dor de cabeça'
            }
        },
        'app/security.py': {
            'bad_chars': {
                'inv�lido': 'inválido',
                'inv\xe1lido': 'inválido',
                'Token inv�lido': 'Token inválido'
            }
        },
        'app/services/validation_service.py': {
            'bad_chars': {
                'ap�s': 'após',
                'ap\xf3s': 'após',
                'deve ser ap�s': 'deve ser após'
            }
        }
    }
    
    print("🚀 CORREÇÃO RÁPIDA DE ENCODING")
    print("=" * 50)
    
    for file_path_str, fixes in file_fixes.items():
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {file_path}")
            continue
        
        print(f"\n🔍 Processando {file_path}...")
        
        # Tentar corrigir encoding
        if fix_encoding_with_fallback(file_path):
            # Aplicar correções específicas
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Aplicar substituições específicas
                for bad_char, good_char in fixes['bad_chars'].items():
                    if bad_char in content:
                        content = content.replace(bad_char, good_char)
                        print(f"   🔄 Substituído: '{bad_char}' → '{good_char}'")
                
                # Salvar conteúdo corrigido
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ Arquivo corrigido com sucesso!")
                
            except Exception as e:
                print(f"   ❌ Erro ao aplicar correções específicas: {e}")
        else:
            print(f"   ❌ Falha ao corrigir encoding")


def add_utf8_headers():
    """Adiciona headers UTF-8 aos arquivos se necessário"""
    files_to_fix = [
        'app/config.py',
        'app/services/ml_model_service.py',
        'app/security.py',
        'app/services/validation_service.py'
    ]
    
    print("\n📝 Adicionando headers UTF-8...")
    
    for file_path_str in files_to_fix:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Verificar se já tem header UTF-8
            has_header = False
            for line in lines[:3]:
                if 'coding:' in line or 'encoding:' in line:
                    has_header = True
                    break
            
            if not has_header:
                print(f"   📝 Adicionando header a {file_path}")
                
                # Adicionar header UTF-8
                if lines and lines[0].startswith('#!'):
                    lines.insert(1, '# -*- coding: utf-8 -*-\n')
                else:
                    lines.insert(0, '# -*- coding: utf-8 -*-\n')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            
        except Exception as e:
            print(f"   ❌ Erro ao processar {file_path}: {e}")


def verify_fixes():
    """Verifica se as correções funcionaram"""
    files_to_verify = [
        'app/config.py',
        'app/services/ml_model_service.py', 
        'app/security.py',
        'app/services/validation_service.py'
    ]
    
    print("\n🔍 VERIFICANDO CORREÇÕES...")
    print("=" * 40)
    
    all_ok = True
    
    for file_path_str in files_to_verify:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {file_path}")
            all_ok = False
            continue
        
        try:
            # Tentar ler como UTF-8
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Tentar compilar como Python
            compile(content, str(file_path), 'exec')
            
            print(f"✅ {file_path}: OK")
            
        except UnicodeDecodeError as e:
            print(f"❌ {file_path}: Erro de encoding - {e}")
            all_ok = False
        except SyntaxError as e:
            if 'utf-8' in str(e).lower():
                print(f"❌ {file_path}: Ainda tem problema de UTF-8 - {e}")
                all_ok = False
            else:
                print(f"⚠️  {file_path}: Erro de sintaxe (não relacionado a encoding) - {e}")
        except Exception as e:
            print(f"❌ {file_path}: Erro inesperado - {e}")
            all_ok = False
    
    return all_ok


def main():
    """Função principal"""
    print("🎯 CORREÇÃO RÁPIDA DE PROBLEMAS DE ENCODING")
    print("Corrigindo os arquivos específicos mencionados no pytest...")
    print()
    
    # 1. Corrigir encoding dos arquivos problemáticos
    fix_specific_encoding_issues()
    
    # 2. Adicionar headers UTF-8
    add_utf8_headers()
    
    # 3. Verificar se as correções funcionaram
    if verify_fixes():
        print("\n🎉 SUCESSO! Todos os arquivos foram corrigidos.")
        print("\nAgora você pode executar os testes:")
        print("python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing")
    else:
        print("\n⚠️  Alguns arquivos ainda têm problemas.")
        print("Execute o script principal 'fix_encoding_issues.py' para uma correção mais abrangente.")


if __name__ == "__main__":
    main()