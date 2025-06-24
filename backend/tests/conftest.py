"""
Configuração do pytest para os testes.
Este arquivo é automaticamente carregado pelo pytest.
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório backend ao Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

