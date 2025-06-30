# tests/fixtures/patient_data.py
"""
Dados de teste para pacientes - casos realistas para testes.
"""

from datetime import datetime, date
from typing import List, Dict, Any

# CPFs válidos para teste (gerados aleatoriamente)
VALID_CPFS = [
    "11144477735",
    "12345678909",
    "98765432100",
    "11111111111",  # CPF especial válido
    "22222222222",  # CPF especial válido
]

# Pacientes de exemplo com diferentes perfis
SAMPLE_PATIENTS = [
    {
        "name": "João Silva Santos",
        "cpf": VALID_CPFS[0],
        "birth_date": date(1980, 5, 15),
        "gender": "M",
        "phone": "(11) 98765-4321",
        "email": "joao.silva@email.com",
        "address": "Rua das Flores, 123",
        "city": "São Paulo",
        "state": "SP",
        "zip_code": "01234-567",
        "medical_history": {
            "chronic_conditions": ["Hipertensão", "Diabetes Tipo 2"],
            "allergies": ["Penicilina"],
            "medications": [
                {"name": "Metformina", "dosage": "850mg", "frequency": "2x ao dia"},
                {"name": "Losartana", "dosage": "50mg", "frequency": "1x ao dia"}
            ],
            "family_history": {
                "diabetes": True,
                "heart_disease": True,
                "cancer": False,
                "hypertension": True
            },
            "surgeries": [
                {"procedure": "Apendicectomia", "date": "2015-03-20", "complications": False}
            ]
        }
    },
    {
        "name": "Maria Oliveira Costa",
        "cpf": VALID_CPFS[1],
        "birth_date": date(1975, 9, 22),
        "gender": "F",
        "phone": "(21) 99888-7766",
        "email": "maria.oliveira@gmail.com",
        "address": "Av. Atlântica, 456",
        "city": "Rio de Janeiro",
        "state": "RJ",
        "zip_code": "22041-001",
        "medical_history": {
            "chronic_conditions": ["Asma", "Hipotireoidismo"],
            "allergies": ["Dipirona", "Frutos do mar"],
            "medications": [
                {"name": "Levotiroxina", "dosage": "75mcg", "frequency": "1x ao dia"},
                {"name": "Salbutamol", "dosage": "100mcg", "frequency": "se necessário"}
            ],
            "family_history": {
                "diabetes": False,
                "heart_disease": False,
                "cancer": True,  # Mãe com câncer de mama
                "hypertension": False
            },
            "surgeries": []
        }
    },
    {
        "name": "Pedro Henrique Almeida",
        "cpf": VALID_CPFS[2],
        "birth_date": date(2010, 3, 10),  # Paciente pediátrico
        "gender": "M",
        "phone": "(31) 3333-4444",
        "responsible_name": "Ana Paula Almeida",
        "responsible_cpf": "33344455566",
        "responsible_phone": "(31) 98877-6655",
        "email": "ana.almeida@email.com",
        "address": "Rua Minas Gerais, 789",
        "city": "Belo Horizonte",
        "state": "MG",
        "zip_code": "30130-100",
        "medical_history": {
            "chronic_conditions": ["Rinite alérgica"],
            "allergies": ["Ácaros", "Poeira"],
            "medications": [
                {"name": "Loratadina", "dosage": "10mg", "frequency": "1x ao dia"}
            ],
            "vaccinations": {
                "bcg": True,
                "hepatitis_b": True,
                "pentavalent": True,
                "polio": True,
                "pneumococcal": True,
                "rotavirus": True,
                "meningococcal": True,
                "yellow_fever": True,
                "mmr": True,
                "varicella": True,
                "hepatitis_a": True,
                "hpv": False  # Ainda não tem idade
            }
        }
    },
    {
        "name": "Ana Carolina Ferreira",
        "cpf": VALID_CPFS[3],
        "birth_date": date(1995, 12, 8),
        "gender": "F",
        "phone": "(85) 99999-1111",
        "email": "ana.ferreira@outlook.com",
        "address": "Rua do Sol, 321",
        "city": "Fortaleza",
        "state": "CE",
        "zip_code": "60150-150",
        "pregnant": True,
        "pregnancy_week": 28,
        "medical_history": {
            "chronic_conditions": [],
            "allergies": [],
            "medications": [
                {"name": "Ácido fólico", "dosage": "5mg", "frequency": "1x ao dia"},
                {"name": "Sulfato ferroso", "dosage": "40mg", "frequency": "1x ao dia"}
            ],
            "obstetric_history": {
                "gravida": 2,
                "para": 0,
                "abortions": 1,
                "living_children": 0,
                "last_menstrual_period": "2024-08-15",
                "estimated_due_date": "2025-05-22"
            }
        }
    },
    {
        "name": "Roberto Carlos Mendes",
        "cpf": VALID_CPFS[4],
        "birth_date": date(1945, 4, 19),  # Paciente idoso
        "gender": "M",
        "phone": "(48) 3333-2222",
        "email": "roberto.mendes@terra.com.br",
        "address": "Rua XV de Novembro, 1500",
        "city": "Florianópolis",
        "state": "SC",
        "zip_code": "88010-400",
        "medical_history": {
            "chronic_conditions": [
                "Hipertensão",
                "Diabetes Tipo 2",
                "Dislipidemia",
                "Artrose",
                "Glaucoma"
            ],
            "allergies": [],
            "medications": [
                {"name": "Enalapril", "dosage": "10mg", "frequency": "2x ao dia"},
                {"name": "Metformina", "dosage": "1000mg", "frequency": "2x ao dia"},
                {"name": "Sinvastatina", "dosage": "40mg", "frequency": "1x ao dia"},
                {"name": "Glucosamina", "dosage": "1500mg", "frequency": "1x ao dia"},
                {"name": "Timolol colírio", "dosage": "0.5%", "frequency": "2x ao dia"}
            ],
            "family_history": {
                "diabetes": True,
                "heart_disease": True,
                "cancer": True,
                "alzheimer": True
            },
            "surgeries": [
                {"procedure": "Prostatectomia", "date": "2018-11-10", "complications": False},
                {"procedure": "Catarata OD", "date": "2020-06-15", "complications": False},
                {"procedure": "Catarata OE", "date": "2021-03-20", "complications": False}
            ]
        }
    }
]

# Casos de teste inválidos para validação
INVALID_PATIENT_DATA = [
    {
        "description": "Nome muito curto",
        "data": {"name": "Jo", "cpf": "12345678901", "birth_date": "1990-01-01", "gender": "M"},
        "expected_error": "Nome deve ter pelo menos 3 caracteres"
    },
    {
        "description": "CPF inválido",
        "data": {"name": "Teste Silva", "cpf": "12345678901", "birth_date": "1990-01-01", "gender": "M"},
        "expected_error": "CPF inválido"
    },
    {
        "description": "Data de nascimento futura",
        "data": {"name": "Futuro Silva", "cpf": "11144477735", "birth_date": "2030-01-01", "gender": "M"},
        "expected_error": "Data de nascimento não pode ser futura"
    },
    {
        "description": "Gênero inválido",
        "data": {"name": "Teste Silva", "cpf": "11144477735", "birth_date": "1990-01-01", "gender": "X"},
        "expected_error": "Gênero deve ser M ou F"
    },
    {
        "description": "Email inválido",
        "data": {
            "name": "Email Inválido",
            "cpf": "11144477735",
            "birth_date": "1990-01-01",
            "gender": "M",
            "email": "email_invalido"
        },
        "expected_error": "Email inválido"
    },
    {
        "description": "Telefone inválido",
        "data": {
            "name": "Telefone Inválido",
            "cpf": "11144477735",
            "birth_date": "1990-01-01",
            "gender": "M",
            "phone": "123"
        },
        "expected_error": "Telefone inválido"
    },
    {
        "description": "Menor sem responsável",
        "data": {
            "name": "Criança Sem Responsável",
            "cpf": "11144477735",
            "birth_date": date.today().isoformat(),  # Recém-nascido
            "gender": "M"
        },
        "expected_error": "Paciente menor de idade requer responsável"
    }
]

# Dados para teste de busca e filtros
SEARCH_TEST_DATA = {
    "patients_by_condition": [
        {"condition": "Diabetes", "expected_count": 2},
        {"condition": "Hipertensão", "expected_count": 2},
        {"condition": "Asma", "expected_count": 1}
    ],
    "patients_by_age_group": [
        {"min_age": 0, "max_age": 18, "expected_count": 1},
        {"min_age": 18, "max_age": 60, "expected_count": 3},
        {"min_age": 60, "max_age": 100, "expected_count": 1}
    ],
    "patients_by_state": [
        {"state": "SP", "expected_count": 1},
        {"state": "RJ", "expected_count": 1},
        {"state": "MG", "expected_count": 1}
    ]
}

def get_test_patient_by_profile(profile: str) -> Dict[str, Any]:
    """
    Retorna dados de paciente baseado no perfil solicitado.
    
    Profiles disponíveis:
    - adult_male: Homem adulto com condições crônicas
    - adult_female: Mulher adulta
    - pediatric: Paciente pediátrico
    - pregnant: Gestante
    - elderly: Idoso com múltiplas condições
    """
    profile_map = {
        "adult_male": SAMPLE_PATIENTS[0],
        "adult_female": SAMPLE_PATIENTS[1],
        "pediatric": SAMPLE_PATIENTS[2],
        "pregnant": SAMPLE_PATIENTS[3],
        "elderly": SAMPLE_PATIENTS[4]
    }
    return profile_map.get(profile, SAMPLE_PATIENTS[0])

def generate_bulk_patients(count: int) -> List[Dict[str, Any]]:
    """Gera lista de pacientes para testes em massa."""
    patients = []
    for i in range(count):
        base_patient = SAMPLE_PATIENTS[i % len(SAMPLE_PATIENTS)].copy()
        # Modifica para tornar único
        base_patient["name"] = f"{base_patient['name']} {i}"
        base_patient["cpf"] = f"{i:011d}"
        base_patient["email"] = f"patient{i}@test.com"
        patients.append(base_patient)
    return patients