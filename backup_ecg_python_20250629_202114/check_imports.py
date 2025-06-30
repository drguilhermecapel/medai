#!/usr/bin/env python3
"""
Verifica o que o teste está tentando importar
"""
import os

print("=== Verificando test_ai_diagnostic_service.py ===\n")

test_file = "tests/test_ai_diagnostic_service.py"

if os.path.exists(test_file):
    print(f"✅ Arquivo de teste existe: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\n📋 Linhas de import (primeiras 20 linhas):")
    for i, line in enumerate(lines[:20], 1):
        if 'import' in line or line.strip().startswith('from'):
            print(f"   Linha {i}: {line.strip()}")
    
    print("\n📄 Primeiras 30 linhas do arquivo de teste:")
    for i, line in enumerate(lines[:30], 1):
        print(f"{i:3d}: {line.rstrip()}")
else:
    print(f"❌ Arquivo não encontrado: {test_file}")

# Testa import direto
print("\n=== Testando import direto ===")
import sys
sys.path.insert(0, os.getcwd())

try:
    # Tenta importar o módulo
    import app.services.ai_diagnostic_service as ai_service
    print("✅ Módulo importado com sucesso")
    
    # Verifica se DiagnosisCategory está disponível
    if hasattr(ai_service, 'DiagnosisCategory'):
        print("✅ DiagnosisCategory está disponível no módulo")
        print(f"   Tipo: {type(ai_service.DiagnosisCategory)}")
    else:
        print("❌ DiagnosisCategory NÃO está disponível no módulo")
        print(f"   Atributos disponíveis: {[a for a in dir(ai_service) if not a.startswith('_')]}")
    
    # Tenta importar diretamente
    from app.services.ai_diagnostic_service import DiagnosisCategory
    print("✅ Import direto de DiagnosisCategory funcionou!")
    
except ImportError as e:
    print(f"❌ Erro de import: {e}")
    print(f"   Tipo do erro: {type(e)}")
    
except Exception as e:
    print(f"❌ Outro erro: {e}")
    print(f"   Tipo: {type(e)}")

# Verifica __init__.py
print("\n=== Verificando __init__.py do services ===")
init_file = "app/services/__init__.py"
if os.path.exists(init_file):
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"Tamanho: {len(content)} bytes")
    if content.strip():
        print("Conteúdo:")
        print(content[:200] + "..." if len(content) > 200 else content)
    else:
        print("Arquivo está vazio")
else:
    print("Arquivo não existe")