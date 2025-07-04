print('🔧 ADICIONANDO API_V1_STR NO CONFIG...')

# Ler config
with open('backend/app/config.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar API_V1_STR se não existir
if 'API_V1_STR' not in content:
    # Encontrar a classe Settings e adicionar a propriedade
    if 'class Settings' in content:
        # Adicionar após a primeira propriedade
        api_property = '''    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MedAI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Medical AI Platform"
    
'''
        # Inserir após 'class Settings(BaseSettings):'
        content = content.replace(
            'class Settings(BaseSettings):',
            f'class Settings(BaseSettings):\n{api_property}'
        )
        
        with open('backend/app/config.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('✅ API_V1_STR adicionado ao Settings!')
    else:
        print('❌ Classe Settings não encontrada')
else:
    print('✅ API_V1_STR já existe')

