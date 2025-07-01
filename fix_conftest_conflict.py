#!/usr/bin/env python3
"""
Resolve o conflito de conftest.py e executa os testes corretamente
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def identify_conftest_files():
    """Identifica todos os arquivos conftest.py"""
    print("🔍 IDENTIFICANDO ARQUIVOS CONFTEST.PY")
    print("=" * 60)
    
    conftest_files = []
    
    # Buscar em todo o projeto
    for root, dirs, files in os.walk("."):
        if "conftest.py" in files:
            conftest_path = Path(root) / "conftest.py"
            conftest_files.append(conftest_path)
            
            print(f"📄 Encontrado: {conftest_path}")
            
            # Mostrar tamanho e primeiras linhas
            try:
                with open(conftest_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   📏 Tamanho: {len(content)} chars")
                
                # Mostrar primeiras 3 linhas não vazias
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                for i, line in enumerate(lines[:3]):
                    print(f"   {i+1:2}: {line}")
                print()
                
            except Exception as e:
                print(f"   ❌ Erro ao ler: {e}")
    
    return conftest_files


def resolve_conftest_conflict(conftest_files):
    """Resolve o conflito mantendo apenas um conftest.py"""
    print("🔧 RESOLVENDO CONFLITO DE CONFTEST.PY")
    print("=" * 60)
    
    if len(conftest_files) <= 1:
        print("✅ Nenhum conflito encontrado")
        return True
    
    # Identificar qual manter
    root_conftest = None
    backend_conftest = None
    
    for conftest in conftest_files:
        if str(conftest) == "tests/conftest.py":
            root_conftest = conftest
        elif "backend" in str(conftest):
            backend_conftest = conftest
    
    print(f"📄 Conftest na raiz: {root_conftest}")
    print(f"📄 Conftest no backend: {backend_conftest}")
    
    # Estratégia: manter o da raiz, fazer backup do backend
    if root_conftest and backend_conftest:
        print("\n🔄 Fazendo backup do conftest do backend...")
        
        backup_path = backend_conftest.with_suffix('.py.backup')
        shutil.copy2(backend_conftest, backup_path)
        print(f"   💾 Backup criado: {backup_path}")
        
        # Remover o conftest do backend
        backend_conftest.unlink()
        print(f"   🗑️  Removido: {backend_conftest}")
    
    elif backend_conftest and not root_conftest:
        print("\n🔄 Movendo conftest do backend para a raiz...")
        
        # Criar diretório tests na raiz se não existir
        Path("tests").mkdir(exist_ok=True)
        
        # Mover conftest do backend para a raiz
        new_location = Path("tests/conftest.py")
        shutil.move(backend_conftest, new_location)
        print(f"   📁 Movido para: {new_location}")
    
    print("✅ Conflito de conftest.py resolvido")
    return True


def create_minimal_conftest():
    """Cria um conftest.py mínimo e funcional"""
    print("\n📝 CRIANDO CONFTEST.PY MÍNIMO")
    print("=" * 60)
    
    conftest_content = '''# -*- coding: utf-8 -*-
"""
Configuração global de testes para MedAI
"""
import pytest
import asyncio
import os
import sys
from pathlib import Path

# Configurar ambiente de teste
os.environ["TESTING"] = "true"
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test_medai.db"

# Adicionar app ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def event_loop():
    """Event loop para testes assíncronos"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_settings():
    """Settings para testes"""
    from app.config import Settings
    return Settings(
        TESTING=True,
        DATABASE_URL="sqlite:///./test_medai.db",
        SECRET_KEY="test-secret-key"
    )

@pytest.fixture
def test_db():
    """Database de teste"""
    from app.database import Base, engine, SessionLocal
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar sessão
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Limpar tabelas após teste
        Base.metadata.drop_all(bind=engine)
'''
    
    # Salvar conftest.py na raiz do projeto de testes
    conftest_path = Path("tests/conftest.py")
    conftest_path.parent.mkdir(exist_ok=True)
    
    with open(conftest_path, 'w', encoding='utf-8') as f:
        f.write(conftest_content)
    
    print(f"✅ Criado: {conftest_path}")


def test_pytest_discovery():
    """Testa se pytest agora consegue descobrir os testes"""
    print("\n🧪 TESTANDO DESCOBERTA DE TESTES")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Código de saída: {result.returncode}")
        
        if result.returncode == 0:
            # Contar testes descobertos
            output_lines = result.stdout.split('\n')
            collected_line = [line for line in output_lines if 'collected' in line]
            
            if collected_line:
                print(f"✅ {collected_line[0]}")
                return True
            else:
                print("✅ Sem erros, mas nenhum teste coletado")
                return True
        else:
            print("❌ Erro na descoberta:")
            for line in result.stderr.split('\n')[:10]:
                if line.strip():
                    print(f"   {line}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout na descoberta de testes")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def run_specific_tests():
    """Executa testes específicos que sabemos que funcionam"""
    print("\n🧪 EXECUTANDO TESTES ESPECÍFICOS")
    print("=" * 60)
    
    # Lista de testes para executar
    test_commands = [
        # Teste simples que já funcionou
        ["python", "-m", "pytest", "tests/test_simple_verification.py", "-v"],
        
        # Teste de config específico
        ["python", "-m", "pytest", "tests/unit/test_config.py", "-v"],
        
        # Todos os testes com timeout
        ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short", "--maxfail=3"]
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{i}️⃣ {' '.join(cmd)}")
        print("-" * 50)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ SUCESSO!")
                
                # Mostrar resumo
                lines = result.stdout.split('\n')
                summary_lines = [line for line in lines if 'passed' in line or 'failed' in line or '=' in line]
                for line in summary_lines[-3:]:
                    if line.strip():
                        print(f"   {line}")
                
                # Se chegou até aqui com sucesso, continue para o próximo
                continue
                
            else:
                print(f"❌ Falhou (código {result.returncode})")
                
                # Mostrar apenas erros importantes
                error_lines = result.stderr.split('\n')
                for line in error_lines[:5]:
                    if line.strip() and 'error' in line.lower():
                        print(f"   {line}")
                
                # Se este comando falhou, tentar o próximo
                continue
                
        except subprocess.TimeoutExpired:
            print("⏱️ Timeout - teste muito lento")
            continue
        except Exception as e:
            print(f"❌ Erro: {e}")
            continue
    
    print("\n🎯 Tente executar manualmente:")
    print("python -m pytest tests/unit/test_config.py -v")


def main():
    """Função principal para resolver o conflito e executar testes"""
    print("🚀 RESOLVENDO CONFLITO DE CONFTEST E EXECUTANDO TESTES")
    print("=" * 70)
    
    # 1. Identificar arquivos conftest.py
    conftest_files = identify_conftest_files()
    
    # 2. Resolver conflito
    resolve_conftest_conflict(conftest_files)
    
    # 3. Criar conftest mínimo se necessário
    if not Path("tests/conftest.py").exists():
        create_minimal_conftest()
    
    # 4. Testar descoberta
    discovery_ok = test_pytest_discovery()
    
    # 5. Executar testes específicos
    if discovery_ok:
        run_specific_tests()
    else:
        print("\n⚠️ Problemas na descoberta, mas vamos tentar executar testes específicos...")
        run_specific_tests()
    
    print("\n" + "=" * 70)
    print("🎯 COMANDOS FINAIS PARA TESTAR:")
    print("=" * 70)
    print("# Teste básico que deve funcionar:")
    print("python -m pytest tests/test_simple_verification.py -v")
    print()
    print("# Teste de configuração:")
    print("python -m pytest tests/unit/test_config.py -v")
    print()
    print("# Todos os testes unitários:")
    print("python -m pytest tests/unit/ -v --tb=short")
    print()
    print("# Com cobertura:")
    print("python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing")


if __name__ == "__main__":
    main()