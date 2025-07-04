import subprocess
import sys

def test_basic_imports():
    """Testa imports básicos"""
    try:
        # Testar import do UserRole
        from app.core.constants import UserRole
        assert hasattr(UserRole, 'VIEWER'), "VIEWER não encontrado em UserRole"
        print("✅ UserRole.VIEWER - OK")
        
        # Testar import do config
        from app.config import Settings
        print("✅ Config - OK")
        
        # Testar import do health
        from app.health import check_database_health
        print("✅ Health module - OK")
        
        # Testar ValidationError
        from app.services.validation_service import ValidationError
        print("✅ ValidationError - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro de import: {e}")
        return False

def test_syntax_errors():
    """Testa se ainda há erros de sintaxe"""
    problem_files = [
        'tests/test_integration_comprehensive.py',
        'tests/test_ml_model_service_enhanced.py'
    ]
    
    for file_path in problem_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            compile(content, file_path, 'exec')
            print(f"✅ {file_path} - Sintaxe OK")
            
        except SyntaxError as e:
            print(f"❌ {file_path} - Ainda tem erro: {e}")
            return False
        except FileNotFoundError:
            print(f"⚠️ {file_path} - Arquivo não encontrado")
    
    return True

print("🔍 VALIDANDO CORREÇÕES...")
print("=" * 50)

imports_ok = test_basic_imports()
syntax_ok = test_syntax_errors()

if imports_ok and syntax_ok:
    print("\n✅ TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
    print("🎯 Pronto para executar testes novamente")
else:
    print("\n❌ Ainda há problemas. Verifique os erros acima.")

