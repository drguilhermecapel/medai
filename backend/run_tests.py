#!/usr/bin/env python3
"""
Script principal para execução de testes do MedAI
Executa todos os testes e gera relatório de cobertura
"""
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Tuple
import json


class TestRunner:
    """Executor de testes com relatório de cobertura"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.coverage_threshold = {
            "global": 80,
            "critical": 100
        }
        self.critical_modules = [
            "app.core.security",
            "app.core.config",
            "app.services.validation_service",
            "app.services.ml_model_service",
            "app.services.patient_service",
            "app.services.exam_service",
            "app.services.diagnostic_service",
            "app.api.v1.endpoints.auth"
        ]
        
    def setup_environment(self):
        """Configura ambiente de testes"""
        print("🔧 Configurando ambiente de testes...")
        
        # Define variáveis de ambiente
        os.environ["TESTING"] = "true"
        os.environ["DATABASE_URL"] = "sqlite:///./test_medai.db"
        os.environ["SECRET_KEY"] = "test-secret-key"
        os.environ["ENVIRONMENT"] = "testing"
        
        # Cria diretórios necessários
        dirs_to_create = [
            self.project_root / "htmlcov",
            self.project_root / "test_reports",
            self.project_root / "ml_models",
            self.project_root / "uploads"
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(exist_ok=True)
            
    def install_dependencies(self):
        """Instala dependências de teste se necessário"""
        print("📦 Verificando dependências...")
        
        test_deps = [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "pytest-timeout>=2.1.0",
            "httpx>=0.24.0",
            "faker>=18.0.0"
        ]
        
        for dep in test_deps:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                print(f"⚠️ Erro ao instalar {dep}")
                
    def run_unit_tests(self) -> Tuple[bool, Dict]:
        """Executa testes unitários"""
        print("\n🧪 Executando testes unitários...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_core_modules.py",
            "tests/test_validation_service.py",
            "tests/test_ml_model_service.py",
            "tests/test_models.py",
            "tests/test_schemas.py",
            "tests/test_repositories.py",
            "tests/test_services.py",
            "tests/test_utilities.py",
            "-v",
            "--cov=app",
            "--cov-report=json",
            "-m", "not integration and not e2e"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0, self._parse_coverage_json()
        
    def run_integration_tests(self) -> Tuple[bool, Dict]:
        """Executa testes de integração"""
        print("\n🔗 Executando testes de integração...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_integration.py",
            "tests/test_auth_endpoints.py",
            "-v",
            "--cov=app",
            "--cov-report=json",
            "--cov-append",
            "-m", "integration or not unit"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0, self._parse_coverage_json()
        
    def run_e2e_tests(self) -> Tuple[bool, Dict]:
        """Executa testes end-to-end"""
        print("\n🌐 Executando testes E2E...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_e2e_comprehensive.py",
            "-v",
            "--cov=app",
            "--cov-report=json",
            "--cov-append",
            "-m", "e2e or not unit"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0, self._parse_coverage_json()
        
    def run_all_tests(self) -> Tuple[bool, Dict]:
        """Executa todos os testes"""
        print("\n🚀 Executando todos os testes...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Erros:", result.stderr)
            
        return result.returncode == 0, self._parse_coverage_json()
        
    def _parse_coverage_json(self) -> Dict:
        """Parse do arquivo JSON de cobertura"""
        coverage_file = self.project_root / "coverage.json"
        
        if not coverage_file.exists():
            return {}
            
        with open(coverage_file, 'r') as f:
            data = json.load(f)
            
        return data
        
    def analyze_coverage(self, coverage_data: Dict) -> Dict:
        """Analisa dados de cobertura"""
        if not coverage_data:
            return {
                "global_coverage": 0,
                "critical_coverage": {},
                "missing_coverage": []
            }
            
        # Cobertura global
        totals = coverage_data.get("totals", {})
        total_statements = totals.get("num_statements", 0)
        covered_statements = totals.get("covered_lines", 0)
        
        global_coverage = (covered_statements / total_statements * 100) if total_statements > 0 else 0
        
        # Cobertura de módulos críticos
        critical_coverage = {}
        files = coverage_data.get("files", {})
        
        for module in self.critical_modules:
            module_path = module.replace(".", "/") + ".py"
            
            for file_path, file_data in files.items():
                if module_path in file_path:
                    summary = file_data.get("summary", {})
                    percent_covered = summary.get("percent_covered", 0)
                    critical_coverage[module] = percent_covered
                    break
            else:
                critical_coverage[module] = 0
                
        # Arquivos com baixa cobertura
        missing_coverage = []
        for file_path, file_data in files.items():
            summary = file_data.get("summary", {})
            percent = summary.get("percent_covered", 0)
            
            if percent < 80:
                missing_coverage.append({
                    "file": file_path,
                    "coverage": percent,
                    "missing_lines": file_data.get("missing_lines", [])
                })
                
        return {
            "global_coverage": global_coverage,
            "critical_coverage": critical_coverage,
            "missing_coverage": missing_coverage
        }
        
    def generate_report(self, coverage_analysis: Dict):
        """Gera relatório de cobertura"""
        print("\n" + "=" * 60)
        print("RELATÓRIO DE COBERTURA - MedAI")
        print("=" * 60)
        
        global_cov = coverage_analysis["global_coverage"]
        global_pass = global_cov >= self.coverage_threshold["global"]
        
        print(f"\n{'✅' if global_pass else '❌'} Cobertura Global: {global_cov:.1f}% (Meta: {self.coverage_threshold['global']}%)")
        
        print("\n📊 Componentes Críticos (Meta: 100%):\n")
        
        all_critical_pass = True
        for module, coverage in coverage_analysis["critical_coverage"].items():
            module_pass = coverage >= self.coverage_threshold["critical"]
            all_critical_pass &= module_pass
            
            status = "✅" if module_pass else "❌"
            module_name = module.split(".")[-1]
            print(f"  {status} {module_name}: {coverage:.1f}%")
            
        if coverage_analysis["missing_coverage"]:
            print("\n⚠️ Arquivos com baixa cobertura:")
            for file_info in coverage_analysis["missing_coverage"][:5]:  # Top 5
                file_name = Path(file_info["file"]).name
                print(f"  - {file_name}: {file_info['coverage']:.1f}%")
                
        print("\n" + "-" * 60)
        
        success = global_pass and all_critical_pass
        
        if success:
            print("✅ SUCESSO: Todas as metas de cobertura foram atingidas!")
        else:
            print("❌ FALHA: Metas de cobertura não atingidas.")
            
            if not global_pass:
                print(f"   - Cobertura global abaixo de {self.coverage_threshold['global']}% ({global_cov:.1f}%)")
                
            if not all_critical_pass:
                print("   - Alguns componentes críticos não atingiram 100% de cobertura")
                
        print("\n📄 Relatório HTML disponível em: htmlcov/index.html")
        
        return success
        
    def create_test_fixtures(self):
        """Cria fixtures necessárias para testes"""
        print("🔨 Criando fixtures de teste...")
        
        # Cria banco de dados de teste
        from app.core.database import Base, engine
        Base.metadata.create_all(bind=engine)
        
        # Cria modelos ML de teste
        ml_models_dir = self.project_root / "ml_models"
        ml_models_dir.mkdir(exist_ok=True)
        
        # Cria arquivo de configuração de teste
        test_env = self.project_root / ".env.test"
        test_env.write_text("""
DATABASE_URL=sqlite:///./test_medai.db
SECRET_KEY=test-secret-key
ENVIRONMENT=testing
DEBUG=True
TESTING=True
""")
        
    def cleanup(self):
        """Limpa arquivos temporários"""
        print("\n🧹 Limpando arquivos temporários...")
        
        temp_files = [
            self.project_root / "test_medai.db",
            self.project_root / ".coverage",
            self.project_root / "coverage.json",
            self.project_root / ".env.test"
        ]
        
        for file in temp_files:
            if file.exists():
                file.unlink()
                
    def run(self, test_type: str = "all"):
        """Executa o processo completo de testes"""
        print("🚀 Iniciando execução de testes MedAI...")
        
        # Setup
        self.setup_environment()
        self.install_dependencies()
        self.create_test_fixtures()
        
        # Executa testes baseado no tipo
        success = False
        coverage_data = {}
        
        try:
            if test_type == "unit":
                success, coverage_data = self.run_unit_tests()
            elif test_type == "integration":
                success, coverage_data = self.run_integration_tests()
            elif test_type == "e2e":
                success, coverage_data = self.run_e2e_tests()
            else:  # all
                success, coverage_data = self.run_all_tests()
                
            # Analisa cobertura
            coverage_analysis = self.analyze_coverage(coverage_data)
            
            # Gera relatório
            coverage_success = self.generate_report(coverage_analysis)
            
            # Sucesso final
            final_success = success and coverage_success
            
        except Exception as e:
            print(f"\n❌ Erro durante execução dos testes: {str(e)}")
            final_success = False
            
        finally:
            # Cleanup
            self.cleanup()
            
        # Exit code
        sys.exit(0 if final_success else 1)


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Executor de testes MedAI")
    parser.add_argument(
        "type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "e2e"],
        help="Tipo de teste a executar"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Não limpar arquivos temporários após execução"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.no_cleanup:
        runner.cleanup = lambda: None
        
    runner.run(args.type)


if __name__ == "__main__":
    main()