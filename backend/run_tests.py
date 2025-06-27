#!/usr/bin/env python3
"""
Script principal para executar testes do MedAI com cobertura
Garante 80% de cobertura global e 100% em testes críticos
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Adiciona o diretório backend ao Python path
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

class TestRunner:
    """Gerenciador de execução de testes com análise de cobertura"""
    
    def __init__(self):
        self.backend_dir = BACKEND_DIR
        self.coverage_file = self.backend_dir / "coverage.json"
        self.critical_modules = [
            "app.services.ecg_analyzer",
            "app.services.ai_diagnosis",
            "app.services.medication_checker",
            "app.services.lab_analyzer",
            "app.services.report_generator",
            "app.api.endpoints.critical",
            "app.utils.medical_calculations",
        ]
        
    def setup_environment(self):
        """Configura variáveis de ambiente para testes"""
        os.environ["PYTHONPATH"] = str(self.backend_dir)
        os.environ["TESTING"] = "true"
        os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/medai_test"
        os.environ["REDIS_URL"] = "redis://localhost:6379/1"
        os.environ["SECRET_KEY"] = "test-secret-key"
        os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"
        
    def run_tests(self, test_type: str = "all") -> int:
        """Executa testes com cobertura"""
        cmd = [
            sys.executable, "-m", "pytest",
            "-v", "--tb=short",
            "--cov=app",
            "--cov-branch",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=json:coverage.json",
        ]
        
        if test_type == "unit":
            cmd.extend(["-m", "unit"])
        elif test_type == "integration":
            cmd.extend(["-m", "integration"])
        elif test_type == "critical":
            cmd.extend(["-m", "critical", "--cov-fail-under=100"])
        
        print(f"Executando testes ({test_type})...")
        result = subprocess.run(cmd, cwd=self.backend_dir)
        return result.returncode
        
    def analyze_coverage(self) -> Tuple[float, Dict[str, float]]:
        """Analisa a cobertura de código"""
        if not self.coverage_file.exists():
            print("Arquivo de cobertura não encontrado!")
            return 0.0, {}
            
        with open(self.coverage_file, 'r') as f:
            coverage_data = json.load(f)
            
        total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
        
        critical_coverage = {}
        files = coverage_data.get("files", {})
        
        for module in self.critical_modules:
            module_path = module.replace(".", "/") + ".py"
            for file_path, file_data in files.items():
                if module_path in file_path:
                    critical_coverage[module] = file_data.get("summary", {}).get("percent_covered", 0)
                    
        return total_coverage, critical_coverage
        
    def check_coverage_requirements(self) -> bool:
        """Verifica se os requisitos de cobertura foram atendidos"""
        total_coverage, critical_coverage = self.analyze_coverage()
        
        print("\n" + "="*60)
        print("RELATÓRIO DE COBERTURA")
        print("="*60)
        
        # Cobertura global
        print(f"\nCobertura Global: {total_coverage:.2f}%")
        if total_coverage < 80:
            print(f"❌ Meta não atingida! (Necessário: 80%)")
        else:
            print(f"✅ Meta atingida!")
            
        # Cobertura dos módulos críticos
        print("\nCobertura dos Módulos Críticos:")
        all_critical_covered = True
        
        for module, coverage in critical_coverage.items():
            status = "✅" if coverage >= 100 else "❌"
            print(f"  {status} {module}: {coverage:.2f}%")
            if coverage < 100:
                all_critical_covered = False
                
        print("="*60)
        
        return total_coverage >= 80 and all_critical_covered
        
    def generate_missing_tests_report(self):
        """Gera relatório de testes faltantes"""
        print("\nGerando relatório de testes faltantes...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=app",
            "--cov-report=term-missing:skip-covered",
            "--quiet"
        ]
        
        subprocess.run(cmd, cwd=self.backend_dir)
        
    def run(self):
        """Executa o processo completo de testes"""
        self.setup_environment()
        
        # Executa todos os testes
        print("🔍 Executando todos os testes...")
        result = self.run_tests("all")
        
        if result != 0:
            print("\n❌ Alguns testes falharam!")
            return 1
            
        # Executa testes críticos com requisito de 100%
        print("\n🏥 Executando testes críticos (requer 100% de cobertura)...")
        result = self.run_tests("critical")
        
        if result != 0:
            print("\n❌ Testes críticos não atingiram 100% de cobertura!")
            self.generate_missing_tests_report()
            return 1
            
        # Verifica requisitos de cobertura
        if not self.check_coverage_requirements():
            print("\n❌ Requisitos de cobertura não atendidos!")
            self.generate_missing_tests_report()
            return 1
            
        print("\n✅ Todos os requisitos de cobertura foram atendidos!")
        print(f"\n📊 Relatório HTML disponível em: {self.backend_dir}/htmlcov/index.html")
        return 0

if __name__ == "__main__":
    runner = TestRunner()
    sys.exit(runner.run())