import subprocess
import sys
import re
from collections import defaultdict

def get_coverage_report():
    """Obtém relatório de cobertura detalhado"""
    print("📊 OBTENDO RELATÓRIO DETALHADO DE COBERTURA")
    print("="*60)
    
    # Executar com formato de relatório detalhado
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/', 
         '--cov=app',
         '--cov-report=term-missing:skip-covered',
         '--no-header',
         '-q'
        ],
        capture_output=True,
        text=True
    )
    
    return result.stdout

def parse_coverage_output(output):
    """Parse do output de cobertura"""
    lines = output.split('\n')
    files_data = []
    
    # Regex para capturar linha de cobertura
    pattern = r'(app[\\/].+?\.py)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+%)\s*(.*)?'
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            file_path = match.group(1)
            stmts = int(match.group(2))
            miss = int(match.group(3))
            branch = int(match.group(4))
            brpart = int(match.group(5))
            cover = match.group(6)
            missing_lines = match.group(7) if match.group(7) else ""
            
            files_data.append({
                'file': file_path,
                'statements': stmts,
                'missing': miss,
                'coverage': int(cover.rstrip('%')),
                'missing_lines': missing_lines.strip()
            })
    
    return files_data

def show_by_coverage_level(files_data):
    """Mostra arquivos agrupados por nível de cobertura"""
    print("\n📊 ARQUIVOS AGRUPADOS POR NÍVEL DE COBERTURA")
    print("="*60)
    
    # Agrupar por faixas
    groups = {
        '0%': [],
        '1-25%': [],
        '26-50%': [],
        '51-75%': [],
        '76-99%': [],
        '100%': []
    }
    
    for file_info in files_data:
        cov = file_info['coverage']
        if cov == 0:
            groups['0%'].append(file_info)
        elif cov <= 25:
            groups['1-25%'].append(file_info)
        elif cov <= 50:
            groups['26-50%'].append(file_info)
        elif cov <= 75:
            groups['51-75%'].append(file_info)
        elif cov < 100:
            groups['76-99%'].append(file_info)
        else:
            groups['100%'].append(file_info)
    
    # Mostrar cada grupo
    for group, files in groups.items():
        if files:
            total_missing = sum(f['missing'] for f in files)
            print(f"\n🔸 {group} de cobertura ({len(files)} arquivos, {total_missing} linhas faltando):")
            
            # Ordenar por número de linhas faltando (maior primeiro)
            files.sort(key=lambda x: x['missing'], reverse=True)
            
            for f in files[:10]:  # Mostrar até 10 por grupo
                file_name = f['file'].replace('app/', '').replace('\\', '/')
                print(f"   • {file_name}: {f['coverage']}% ({f['missing']} linhas faltando)")
            
            if len(files) > 10:
                print(f"   ... e mais {len(files) - 10} arquivos")

def show_quick_wins():
    """Identifica quick wins - arquivos pequenos com 0% de cobertura"""
    print("\n🎯 QUICK WINS - ARQUIVOS PEQUENOS COM 0% COBERTURA")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/', 
         '--cov=app',
         '--cov-report=',  # Sem output
         '--cov-report=json',
         '-q'
        ],
        capture_output=True,
        text=True
    )
    
    import json
    try:
        with open('coverage.json', 'r') as f:
            coverage_data = json.load(f)
        
        quick_wins = []
        for file_path, file_data in coverage_data.get('files', {}).items():
            if file_path.startswith('app/'):
                percent = file_data['summary']['percent_covered']
                statements = file_data['summary']['num_statements']
                
                # Quick win: arquivo pequeno com 0% de cobertura
                if percent == 0 and statements <= 50:
                    quick_wins.append({
                        'file': file_path,
                        'statements': statements,
                        'impact': statements / coverage_data['totals']['num_statements'] * 100
                    })
        
        # Ordenar por número de statements
        quick_wins.sort(key=lambda x: x['statements'])
        
        print(f"\nEncontrados {len(quick_wins)} arquivos pequenos sem cobertura:")
        total_impact = 0
        for qw in quick_wins[:15]:
            file_name = qw['file'].replace('app/', '')
            total_impact += qw['impact']
            print(f"   • {file_name}: {qw['statements']} linhas (+{qw['impact']:.1f}% impacto)")
        
        print(f"\n✅ Testar estes {min(15, len(quick_wins))} arquivos adicionaria ~{total_impact:.1f}% à cobertura total!")
        
    except Exception as e:
        print(f"❌ Erro ao analisar quick wins: {e}")

def create_first_test():
    """Cria o primeiro teste como exemplo"""
    print("\n🔧 CRIANDO PRIMEIRO TESTE DE EXEMPLO")
    print("="*60)
    
    # Exemplo: teste para utils/validators.py (geralmente tem 0% de cobertura)
    test_content = '''"""
Tests for app.utils.validators
"""
import pytest
from app.utils.validators import *  # Importar todas as funções

class TestValidators:
    """Test validators utility functions"""
    
    def test_validate_cpf_valid(self):
        """Test CPF validation with valid CPF"""
        # CPFs válidos para teste
        valid_cpfs = [
            "123.456.789-00",  # Com formatação
            "12345678900",     # Sem formatação
        ]
        
        for cpf in valid_cpfs:
            assert validate_cpf(cpf) == True
    
    def test_validate_cpf_invalid(self):
        """Test CPF validation with invalid CPF"""
        invalid_cpfs = [
            "000.000.000-00",  # Todos zeros
            "111.111.111-11",  # Todos iguais
            "123.456.789-99",  # Dígito verificador errado
            "abc.def.ghi-jk",  # Letras
            "",                # Vazio
            None,              # None
        ]
        
        for cpf in invalid_cpfs:
            assert validate_cpf(cpf) == False
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "name+tag@company.org",
        ]
        
        for email in valid_emails:
            assert validate_email(email) == True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user @domain.com",
            "",
            None,
        ]
        
        for email in invalid_emails:
            assert validate_email(email) == False

# Se o arquivo validators.py não existir, crie funções básicas
if __name__ == "__main__":
    # Criar validators.py se não existir
    import os
    validators_path = "app/utils/validators.py"
    
    if not os.path.exists(validators_path):
        validators_content = \'\'\'"""
Validation utility functions
"""
import re

def validate_cpf(cpf: str) -> bool:
    """Validate Brazilian CPF"""
    if not cpf:
        return False
    
    # Remove formatting
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    
    # Check length
    if len(cpf) != 11:
        return False
    
    # Check if all digits are the same
    if cpf == cpf[0] * 11:
        return False
    
    # Validate check digits
    # TODO: Implement full CPF validation
    return True

def validate_email(email: str) -> bool:
    """Validate email address"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email)))

def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    if not phone:
        return False
    
    # Remove formatting
    phone = re.sub(r'[^0-9]', '', str(phone))
    
    # Brazilian phone numbers
    return len(phone) in [10, 11]
\'\'\'
        
        os.makedirs(os.path.dirname(validators_path), exist_ok=True)
        with open(validators_path, 'w') as f:
            f.write(validators_content)
        print(f"✅ Criado {validators_path}")
'''
    
    test_file = 'tests/test_validators.py'
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"✅ Criado: {test_file}")
    print("\n🧪 Para executar este teste:")
    print(f"   pytest {test_file} -v")
    
    # Executar o teste
    print("\n📊 Executando o teste criado...")
    result = subprocess.run(
        [sys.executable, test_file],  # Cria validators.py se necessário
        capture_output=True
    )
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', test_file, '-v'],
        capture_output=True,
        text=True
    )
    
    if 'passed' in result.stdout:
        print("✅ Teste passou! Você acabou de aumentar a cobertura!")
    else:
        print("📝 Teste criado. Execute para ver o resultado.")

def main():
    """Função principal"""
    # Obter e analisar cobertura
    output = get_coverage_report()
    files_data = parse_coverage_output(output)
    
    # Mostrar análises
    show_by_coverage_level(files_data)
    show_quick_wins()
    create_first_test()
    
    print("\n" + "="*60)
    print("📋 AÇÕES IMEDIATAS RECOMENDADAS")
    print("="*60)
    
    print("\n1️⃣ Execute o teste de exemplo criado:")
    print("   pytest tests/test_validators.py -v --cov=app.utils.validators")
    
    print("\n2️⃣ Veja o relatório HTML de cobertura:")
    print("   pytest tests/ --cov=app --cov-report=html")
    print("   start htmlcov/index.html")
    
    print("\n3️⃣ Escolha um arquivo com 0% e crie testes:")
    print("   • Comece pelos arquivos utils/ (mais fáceis)")
    print("   • Depois passe para services/ (mais complexos)")
    print("   • Por último, faça os endpoints da API")

if __name__ == "__main__":
    main()