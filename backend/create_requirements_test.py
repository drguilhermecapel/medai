#!/usr/bin/env python3
"""
Script para criar o arquivo requirements-test.txt corretamente
"""

# Conteúdo do requirements-test.txt
requirements_content = """# Core Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
pytest-mock==3.12.0

# HTTP Testing
httpx==0.25.2

# Test Data
faker==20.1.0

# Database
sqlalchemy-utils==0.41.1

# Coverage
coverage==7.3.4

# Environment
python-dotenv==1.0.0
"""

# Criar o arquivo
with open('requirements-test.txt', 'w', encoding='utf-8') as f:
    f.write(requirements_content.strip())

print("✅ Arquivo requirements-test.txt criado com sucesso!")
print("\nAgora você pode instalar as dependências com:")
print("pip install -r requirements-test.txt")