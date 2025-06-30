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
            "app.services.ai_diagnostic_service",
            "app.services.ml_model_service",
            "app.services.validation_service",
            "app.services.medical_record_service",
            "app.services.prescription_service"]
        
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
            "--cov-report=json:coverage.json"]
        
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
                    break
                    
        return total_coverage, critical_coverage
        
    def generate_report(self, total_coverage: float, critical_coverage: Dict[str, float]):
        """Gera relatório de cobertura"""
        print("\n" + "="*60)
        print("RELATÓRIO DE COBERTURA - MedAI")
        print("="*60)
        
        # Cobertura global
        status = "✅" if total_coverage >= 80 else "❌"
        print(f"\n{status} Cobertura Global: {total_coverage:.1f}% (Meta: 80%)")
        
        # Cobertura de componentes críticos
        print("\n📊 Componentes Críticos (Meta: 100%):")
        all_critical_ok = True
        
        for module, coverage in critical_coverage.items():
            status = "✅" if coverage == 100 else "❌"
            if coverage < 100:
                all_critical_ok = False
            print(f"  {status} {module}: {coverage:.1f}%")
            
        # Resumo
        print("\n" + "-"*60)
        if total_coverage >= 80 and all_critical_ok:
            print("✅ SUCESSO: Todas as metas de cobertura foram atingidas!")
        else:
            print("❌ FALHA: Metas de cobertura não atingidas.")
            if total_coverage < 80:
                print(f"   - Cobertura global abaixo de 80% ({total_coverage:.1f}%)")
            if not all_critical_ok:
                print("   - Componentes críticos sem 100% de cobertura")
                
    def run(self):
        """Executa o processo completo de testes"""
        self.setup_environment()
        
        # Executar todos os testes
        print("🚀 Iniciando execução de testes MedAI...\n")
        return_code = self.run_tests("all")
        
        # Analisar cobertura
        total_coverage, critical_coverage = self.analyze_coverage()
        
        # Gerar relatório
        self.generate_report(total_coverage, critical_coverage)
        
        # Executar testes críticos com falha se não 100%
        if critical_coverage:
            print("\n🔍 Verificando componentes críticos...")
            critical_code = self.run_tests("critical")
            if critical_code != 0:
                return 1
                
        return 0 if return_code == 0 else 1

if __name__ == "__main__":
    runner = TestRunner()
    sys.exit(runner.run())