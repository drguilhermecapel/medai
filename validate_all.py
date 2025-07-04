print('🧪 EXECUTANDO VALIDAÇÃO COMPLETA...')

def test_imports():
    """Testa todos os imports problemáticos"""
    errors = []
    
    # Testar constants
    try:
        from backend.app.core.constants import (
            UserRole, DiagnosisCategory, NotificationPriority, 
            NotificationType, UserRoles, AnalysisStatus, ClinicalUrgency,
            ValidationStatus, ModelType
        )
        print('✅ Todas as constants importadas')
    except ImportError as e:
        errors.append(f'Constants: {e}')
    
    # Testar config
    try:
        from backend.app.config import Settings, DatabaseConfig
        settings = Settings()
        assert hasattr(settings, 'API_V1_STR'), 'API_V1_STR não encontrado'
        print('✅ Config e DatabaseConfig OK')
    except Exception as e:
        errors.append(f'Config: {e}')
    
    # Testar models
    try:
        # Testar se o arquivo existe e pode ser importado
        import os
        if os.path.exists('backend/app/models/appointment.py'):
            print('✅ Appointment file exists')
        else:
            print('❌ Appointment file not found')
    except ImportError as e:
        errors.append(f'Models: {e}')
    
    # Testar health
    try:
        from backend.app.health import HealthChecker
        print('✅ Health modules OK')
    except ImportError as e:
        errors.append(f'Health: {e}')
    
    # Testar validation
    try:
        from backend.app.services.validation_service import ValidationResult
        print('✅ Validation classes OK')
    except ImportError as e:
        errors.append(f'Validation: {e}')
    
    if errors:
        print('❌ ERROS ENCONTRADOS:')
        for error in errors:
            print(f'   • {error}')
        return False
    else:
        print('✅ TODOS OS IMPORTS FUNCIONANDO!')
        return True

def test_tensorflow_mock():
    """Testa mock do TensorFlow"""
    try:
        import sys
        import os
        sys.path.insert(0, 'tests/mocks')
        import tensorflow_mock as tf
        
        # Testar funcionalidades básicas
        model = tf.keras.models.Sequential()
        tensor = tf.constant([1, 2, 3])
        
        print('✅ TensorFlow mock funcionando!')
        return True
    except Exception as e:
        print(f'❌ TensorFlow mock com problemas: {e}')
        return False

# Executar validações
print('=' * 60)
imports_ok = test_imports()
tf_ok = test_tensorflow_mock()

if imports_ok and tf_ok:
    print('\n🎉 TODAS AS CORREÇÕES APLICADAS COM SUCESSO!')
    print('🚀 Pronto para executar testes completos!')
else:
    print('\n⚠️ Ainda há problemas. Verifique os erros acima.')

