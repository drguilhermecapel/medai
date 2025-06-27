# fix_all_issues.py
import os
import re

def fix_constants_file():
    """Adiciona valores faltantes aos enums em constants.py"""
    constants_file = os.path.join('app', 'core', 'constants.py')
    
    with open(constants_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir UserRole
    if 'class UserRole' in content and 'PHYSICIAN = "physician"' not in content:
        content = re.sub(
            r'(class UserRole.*?:.*?\n)',
            r'\1    VIEWER = "viewer"\n    PATIENT = "patient"\n    RECEPTIONIST = "receptionist"\n    NURSE = "nurse"\n    DOCTOR = "doctor"\n',
            content,
            flags=re.DOTALL
        )
    
    # Corrigir AnalysisStatus
    if 'class AnalysisStatus' in content and 'PROCESSING = "processing"' not in content:
        content = re.sub(
            r'(class AnalysisStatus.*?PENDING = "pending"\n)',
            r'\1    PROCESSING = "processing"\n',
            content
        )
    
    # Corrigir ClinicalUrgency
    if 'class ClinicalUrgency' in content and 'MEDIUM = "medium"' not in content:
        content = re.sub(
            r'(class ClinicalUrgency.*?LOW = "low"\n)',
            r'\1    MEDIUM = "medium"\n    ROUTINE = "routine"\n    PRIORITY = "priority"\n    EMERGENCY = "emergency"\n    ELECTIVE = "elective"\n',
            content
        )
    
    # Adicionar ModelType se não existir
    if 'class ModelType' not in content:
        model_type = '''
class ModelType(str, Enum):
    """Tipos de modelo ML"""
    ECG_CLASSIFIER = "ecg_classifier"
    RISK_PREDICTOR = "risk_predictor"
    ARRHYTHMIA_DETECTOR = "arrhythmia_detector"
'''
        # Adicionar antes do export all
        content = re.sub(
            r'(# Export all para facilitar imports)',
            model_type + '\n\1',
            content
        )
        
        # Adicionar ao __all__
        content = re.sub(
            r'("TreatmentType")',
            r'\1,\n    "ModelType"',
            content
        )
    
    with open(constants_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ constants.py atualizado")

def add_extend_existing_to_models():
    """Adiciona extend_existing a todos os modelos"""
    models_dir = os.path.join('app', 'models')
    
    for file in os.listdir(models_dir):
        if file.endswith('.py') and file not in ['__init__.py', 'base.py']:
            filepath = os.path.join(models_dir, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se já tem __table_args__
            if '__table_args__' not in content and '__tablename__' in content:
                # Adicionar após __tablename__
                content = re.sub(
                    r'(__tablename__\s*=\s*["\'][^"\']+["\'])',
                    r"\1\n    __table_args__ = {'extend_existing': True}",
                    content
                )
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ Adicionado extend_existing a {file}")

def fix_service_signatures():
    """Corrige assinaturas de métodos nos serviços"""
    fixes = {
        'app/services/patient_service.py': [
            ('def search_patients\(self, query: str\)', 
             'def search_patients(self, query: str, search_fields: List[str] = None)')
        ],
        'app/services/notification_service.py': [
            ('def mark_as_read\(self, notification_id: int\)',
             'def mark_as_read(self, notification_id: int, user_id: int)')
        ]
    }
    
    for filepath, replacements in fixes.items():
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for old, new in replacements:
                content = re.sub(old, new, content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Corrigidas assinaturas em {filepath}")

def main():
    print("Corrigindo todos os problemas identificados...\n")
    
    # 1. Corrigir constants.py
    fix_constants_file()
    
    # 2. Adicionar extend_existing aos modelos
    add_extend_existing_to_models()
    
    # 3. Corrigir assinaturas de métodos
    fix_service_signatures()
    
    print("\n✅ Todas as correções aplicadas!")
    print("\nAgora execute os testes novamente:")
    print("pytest tests -v --tb=short")

if __name__ == "__main__":
    main()