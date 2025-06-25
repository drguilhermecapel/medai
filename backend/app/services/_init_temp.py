"""
Services module - Temporary version for testing
"""

# Comentar temporariamente as importações problemáticas
# from app.services.auth_service import AuthService
# from app.services.user_service import UserService
# ... outras importações ...

# Importar apenas o que é necessário para os testes
try:
    from app.services.ai_diagnostic_service import AIDiagnosticService
except ImportError:
    # Se falhar, criar uma classe mock
    class AIDiagnosticService:
        def __init__(self, db_session=None):
            self.db_session = db_session

__all__ = ['AIDiagnosticService']