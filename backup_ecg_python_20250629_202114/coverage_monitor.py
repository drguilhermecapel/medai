"""
Script de Monitoramento de Cobertura para MedAI
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import argparse


class CoverageMonitor:
    """Monitor de cobertura de testes para MedAI."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_path = self.project_root / "backend"
        self.frontend_path = self.project_root / "frontend"
        self.reports_path = self.project_root / "coverage_reports"
        self.reports_path.mkdir(exist_ok=True)
        
        # Limites de cobertura
        self.coverage_thresholds = {
            "global": 80,
            "critical_components": 100,
            "services": 95,
            "repositories": 85,
            "api_endpoints": 85
        }
        
        # Componentes críticos que devem ter 100% de cobertura
        self.critical_components = [
            "app/services/ai_diagnostic_service.py",
            "app/services/ml_model_service.py",
            "app/services/validation_service.py",
            "app/services/medical_record_service.py",
            "app/services/prescription_service.py"
        ]

    def run_backend_coverage(self) -> dict:
        """Executa análise de cobertura do backend."""
        print("🔍 Executando análise de cobertura do backend...")
        
        os.chdir(self.backend_path)
        
        # Executar testes com cobertura
        cmd = [
            "python", "-m", "pytest",
            "--cov=app",
            "--cov-report=json:coverage.json",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-fail-under=80",
            "-v"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Ler relatório de cobertura JSON
            coverage_file = self.backend_path / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                return {
                    "success": result.returncode == 0,
                    "coverage_data": coverage_data,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "error": "Arquivo de cobertura não encontrado",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def run_frontend_coverage(self) -> dict:
        """Executa análise de cobertura do frontend."""
        print("🔍 Executando análise de cobertura do frontend...")
        
        os.chdir(self.frontend_path)
        
        # Executar testes com cobertura
        cmd = ["npm", "run", "test:coverage"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Ler relatório de cobertura
            coverage_file = self.frontend_path / "coverage" / "coverage-summary.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                return {
                    "success": result.returncode == 0,
                    "coverage_data": coverage_data,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "error": "Arquivo de cobertura não encontrado"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_critical_components(self, coverage_data: dict) -> dict:
        """Analisa cobertura dos componentes críticos."""
        critical_coverage = {}
        files = coverage_data.get("files", {})
        
        for component in self.critical_components:
            found = False
            for file_path, file_data in files.items():
                if component in file_path or file_path.endswith(component):
                    coverage = file_data.get("summary", {}).get("percent_covered", 0)
                    critical_coverage[component] = coverage
                    found = True
                    break
            
            if not found:
                critical_coverage[component] = 0
                
        return {
            "components": critical_coverage,
            "total_coverage": min(critical_coverage.values()) if critical_coverage else 0,
            "all_100": all(cov == 100 for cov in critical_coverage.values())
        }

    def generate_recommendations(self, coverage_analysis: dict) -> list:
        """Gera recomendações baseadas na análise de cobertura."""
        recommendations = []
        
        # Verifica cobertura global
        global_coverage = coverage_analysis.get("global_coverage", 0)
        if global_coverage < self.coverage_thresholds["global"]:
            recommendations.append({
                "type": "critical",
                "message": f"Cobertura global ({global_coverage:.1f}%) abaixo da meta de {self.coverage_thresholds['global']}%",
                "action": "Adicione mais testes unitários e de integração"
            })
        
        # Verifica componentes críticos
        critical_components = coverage_analysis.get("critical_components", {})
        for component, coverage in critical_components.items():
            if coverage < 100:
                recommendations.append({
                    "type": "critical",
                    "message": f"Componente crítico '{component}' com apenas {coverage:.1f}% de cobertura",
                    "action": f"Adicione testes para cobrir 100% do componente {component}"
                })
        
        # Analisa arquivos com baixa cobertura
        files = coverage_analysis.get("files", {})
        low_coverage_files = []
        
        for file_path, file_data in files.items():
            coverage = file_data.get("summary", {}).get("percent_covered", 0)
            if coverage < 60 and not any(skip in file_path for skip in ["__init__.py", "config.py", "migrations"]):
                low_coverage_files.append((file_path, coverage))
        
        if low_coverage_files:
            low_coverage_files.sort(key=lambda x: x[1])
            worst_files = low_coverage_files[:5]
            
            recommendations.append({
                "type": "warning",
                "message": "Arquivos com cobertura muito baixa detectados",
                "action": "Priorize adicionar testes para: " + ", ".join([f[0] for f in worst_files])
            })
        
        return recommendations

    def generate_report(self, backend_result: dict, frontend_result: dict) -> dict:
        """Gera relatório consolidado de cobertura."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project": "MedAI",
            "backend": {},
            "frontend": {},
            "recommendations": []
        }
        
        # Análise do backend
        if backend_result.get("success"):
            coverage_data = backend_result.get("coverage_data", {})
            totals = coverage_data.get("totals", {})
            
            report["backend"] = {
                "total_coverage": totals.get("percent_covered", 0),
                "lines_covered": totals.get("covered_lines", 0),
                "total_lines": totals.get("num_statements", 0),
                "critical_components": self.analyze_critical_components(coverage_data)
            }
        else:
            report["backend"]["error"] = backend_result.get("error", "Falha desconhecida")
        
        # Análise do frontend
        if frontend_result.get("success"):
            coverage_data = frontend_result.get("coverage_data", {})
            total = coverage_data.get("total", {})
            
            report["frontend"] = {
                "total_coverage": total.get("lines", {}).get("pct", 0),
                "lines_covered": total.get("lines", {}).get("covered", 0),
                "total_lines": total.get("lines", {}).get("total", 0)
            }
        else:
            report["frontend"]["error"] = frontend_result.get("error", "Falha desconhecida")
        
        # Calcula cobertura global
        backend_coverage = report["backend"].get("total_coverage", 0)
        frontend_coverage = report["frontend"].get("total_coverage", 0)
        
        # Média ponderada (backend tem peso maior por ser mais crítico)
        global_coverage = (backend_coverage * 0.7 + frontend_coverage * 0.3)
        
        report["summary"] = {
            "global_coverage": global_coverage,
            "critical_coverage": report["backend"].get("critical_components", {}).get("total_coverage", 0),
            "overall_success": (
                global_coverage >= self.coverage_thresholds["global"] and
                report["backend"].get("critical_components", {}).get("all_100", False)
            )
        }
        
        # Gerar recomendações
        coverage_analysis = {
            "global_coverage": global_coverage,
            "critical_components": report["backend"].get("critical_components", {}).get("components", {}),
            "files": backend_result.get("coverage_data", {}).get("files", {})
        }
        
        report["recommendations"] = self.generate_recommendations(coverage_analysis)
        
        return report

    def save_report(self, report: dict):
        """Salva o relatório de cobertura."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salva JSON
        json_file = self.reports_path / f"coverage_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Salva relatório resumido
        summary_file = self.reports_path / f"coverage_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("RELATÓRIO DE COBERTURA - MedAI\n")
            f.write(f"Data: {report['timestamp']}\n")
            f.write("=" * 60 + "\n\n")
            
            summary = report.get("summary", {})
            f.write(f"Cobertura Global: {summary.get('global_coverage', 0):.1f}%\n")
            f.write(f"Componentes Críticos: {summary.get('critical_coverage', 0):.1f}%\n")
            f.write(f"Status: {'✅ SUCESSO' if summary.get('overall_success') else '❌ FALHA'}\n\n")
            
            if report.get("recommendations"):
                f.write("RECOMENDAÇÕES:\n")
                for rec in report["recommendations"]:
                    f.write(f"\n[{rec['type'].upper()}] {rec['message']}\n")
                    f.write(f"  → {rec['action']}\n")
        
        print(f"\n📊 Relatórios salvos em: {self.reports_path}")
        print(f"  - JSON: {json_file.name}")
        print(f"  - Resumo: {summary_file.name}")

    def run(self):
        """Executa o monitoramento completo."""
        print("🚀 Iniciando monitoramento de cobertura MedAI\n")
        
        # Executa análise do backend
        backend_result = self.run_backend_coverage()
        
        # Executa análise do frontend
        frontend_result = self.run_frontend_coverage()
        
        # Gera relatório consolidado
        report = self.generate_report(backend_result, frontend_result)
        
        # Salva relatórios
        self.save_report(report)
        
        # Exibe resumo
        self.display_summary(report)
        
        # Retorna código de saída
        return 0 if report["summary"]["overall_success"] else 1

    def display_summary(self, report: dict):
        """Exibe resumo do relatório no console."""
        print("\n" + "=" * 60)
        print("RESUMO DE COBERTURA")
        print("=" * 60)
        
        summary = report.get("summary", {})
        backend = report.get("backend", {})
        frontend = report.get("frontend", {})
        
        # Status geral
        status = "✅ SUCESSO" if summary.get("overall_success") else "❌ FALHA"
        print(f"\nStatus Geral: {status}")
        
        # Cobertura global
        print(f"\nCobertura Global: {summary.get('global_coverage', 0):.1f}% (Meta: {self.coverage_thresholds['global']}%)")
        
        # Backend
        if not backend.get("error"):
            print(f"\nBackend:")
            print(f"  - Cobertura Total: {backend.get('total_coverage', 0):.1f}%")
            print(f"  - Linhas Cobertas: {backend.get('lines_covered', 0)}/{backend.get('total_lines', 0)}")
            
            critical = backend.get("critical_components", {})
            print(f"  - Componentes Críticos: {critical.get('total_coverage', 0):.1f}% (Meta: 100%)")
            
            if critical.get("components"):
                for comp, cov in critical["components"].items():
                    status_icon = "✅" if cov == 100 else "❌"
                    print(f"    {status_icon} {comp}: {cov:.1f}%")
        else:
            print(f"\nBackend: ❌ Erro - {backend.get('error')}")
        
        # Frontend
        if not frontend.get("error"):
            print(f"\nFrontend:")
            print(f"  - Cobertura Total: {frontend.get('total_coverage', 0):.1f}%")
            print(f"  - Linhas Cobertas: {frontend.get('lines_covered', 0)}/{frontend.get('total_lines', 0)}")
        else:
            print(f"\nFrontend: ❌ Erro - {frontend.get('error')}")
        
        # Recomendações
        if report.get("recommendations"):
            print("\n📋 RECOMENDAÇÕES:")
            for rec in report["recommendations"]:
                print(f"\n  [{rec['type'].upper()}] {rec['message']}")
                print(f"    → {rec['action']}")
        
        print("\n" + "=" * 60)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Monitor de Cobertura de Testes MedAI")
    parser.add_argument("--project-root", default=".", help="Caminho raiz do projeto")
    parser.add_argument("--backend-only", action="store_true", help="Analisar apenas o backend")
    parser.add_argument("--frontend-only", action="store_true", help="Analisar apenas o frontend")
    args = parser.parse_args()
    
    monitor = CoverageMonitor(args.project_root)
    
    if args.backend_only:
        backend_result = monitor.run_backend_coverage()
        # Processar apenas backend
        report = monitor.generate_report(backend_result, {"success": False, "error": "Não executado"})
    elif args.frontend_only:
        frontend_result = monitor.run_frontend_coverage()
        # Processar apenas frontend
        report = monitor.generate_report({"success": False, "error": "Não executado"}, frontend_result)
    else:
        sys.exit(monitor.run())
    
    monitor.display_summary(report)
    monitor.save_report(report)
    
    sys.exit(0 if report["summary"]["overall_success"] else 1)


if __name__ == "__main__":
    main()