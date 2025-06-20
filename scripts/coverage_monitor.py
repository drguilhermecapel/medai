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
            "app/services/ecg_service.py",
            "app/services/ml_model_service.py", 
            "app/services/ai_diagnostic_service.py",
            "app/services/validation_service.py",
            "app/services/hybrid_ecg_service.py"
        ]

    def run_backend_coverage(self) -> dict:
        """Executa análise de cobertura do backend."""
        print("🔍 Executando análise de cobertura do backend...")
        
        os.chdir(self.backend_path)
        
        # Executar testes com cobertura
        cmd = [
            "python3.11", "-m", "pytest",
            "--cov=app",
            "--cov-report=json:coverage.json",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-fail-under=80",
            "-v"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env={
                **os.environ,
                "PYTHONPATH": str(self.backend_path)
            })
            
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
        
        frontend_path = self.frontend_path
        if not frontend_path.exists():
            return {
                "success": False,
                "error": "Diretório frontend não encontrado"
            }
        
        os.chdir(frontend_path)
        
        # Verificar se package.json existe
        package_json = frontend_path / "package.json"
        if not package_json.exists():
            return {
                "success": False,
                "error": "package.json não encontrado no frontend"
            }
        
        try:
            # Executar testes com cobertura
            cmd = ["npm", "run", "test:coverage"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Procurar por arquivo de cobertura
            coverage_files = [
                frontend_path / "coverage" / "coverage-summary.json",
                frontend_path / "coverage" / "lcov-report" / "index.html"
            ]
            
            coverage_data = None
            for coverage_file in coverage_files:
                if coverage_file.exists() and coverage_file.suffix == ".json":
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    break
            
            return {
                "success": result.returncode == 0,
                "coverage_data": coverage_data,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_critical_components(self, coverage_data: dict) -> dict:
        """Analisa cobertura dos componentes críticos."""
        print("🎯 Analisando cobertura dos componentes críticos...")
        
        critical_analysis = {
            "components": {},
            "overall_critical_coverage": 0,
            "meets_requirements": False
        }
        
        if not coverage_data or "files" not in coverage_data:
            return critical_analysis
        
        files_data = coverage_data["files"]
        critical_coverages = []
        
        for component in self.critical_components:
            # Procurar arquivo nos dados de cobertura
            file_found = False
            for file_path, file_data in files_data.items():
                if component in file_path:
                    coverage_percent = file_data["summary"]["lines"]["pct_covered"]
                    critical_analysis["components"][component] = {
                        "coverage": coverage_percent,
                        "meets_requirement": coverage_percent >= self.coverage_thresholds["critical_components"],
                        "missing_lines": file_data["summary"]["lines"]["num_statements"] - file_data["summary"]["lines"]["covered_lines"]
                    }
                    critical_coverages.append(coverage_percent)
                    file_found = True
                    break
            
            if not file_found:
                critical_analysis["components"][component] = {
                    "coverage": 0,
                    "meets_requirement": False,
                    "error": "Arquivo não encontrado nos dados de cobertura"
                }
                critical_coverages.append(0)
        
        # Calcular cobertura média dos componentes críticos
        if critical_coverages:
            critical_analysis["overall_critical_coverage"] = sum(critical_coverages) / len(critical_coverages)
            critical_analysis["meets_requirements"] = all(
                comp["meets_requirement"] for comp in critical_analysis["components"].values()
            )
        
        return critical_analysis

    def generate_coverage_report(self, backend_result: dict, frontend_result: dict) -> dict:
        """Gera relatório consolidado de cobertura."""
        print("📊 Gerando relatório consolidado de cobertura...")
        
        timestamp = datetime.now()
        
        report = {
            "timestamp": timestamp.isoformat(),
            "summary": {
                "backend_success": backend_result.get("success", False),
                "frontend_success": frontend_result.get("success", False),
                "overall_success": False,
                "global_coverage": 0,
                "critical_coverage": 0
            },
            "backend": {},
            "frontend": {},
            "critical_components": {},
            "recommendations": []
        }
        
        # Analisar backend
        if backend_result.get("success") and backend_result.get("coverage_data"):
            backend_data = backend_result["coverage_data"]
            total_coverage = backend_data.get("totals", {}).get("percent_covered", 0)
            
            report["backend"] = {
                "total_coverage": total_coverage,
                "meets_threshold": total_coverage >= self.coverage_thresholds["global"],
                "lines_covered": backend_data.get("totals", {}).get("covered_lines", 0),
                "lines_total": backend_data.get("totals", {}).get("num_statements", 0)
            }
            
            # Analisar componentes críticos
            critical_analysis = self.analyze_critical_components(backend_data)
            report["critical_components"] = critical_analysis
            report["summary"]["critical_coverage"] = critical_analysis["overall_critical_coverage"]
        
        # Analisar frontend
        if frontend_result.get("success") and frontend_result.get("coverage_data"):
            frontend_data = frontend_result["coverage_data"]
            if "total" in frontend_data:
                total_data = frontend_data["total"]
                frontend_coverage = total_data.get("lines", {}).get("pct", 0)
                
                report["frontend"] = {
                    "total_coverage": frontend_coverage,
                    "meets_threshold": frontend_coverage >= self.coverage_thresholds["global"],
                    "lines_covered": total_data.get("lines", {}).get("covered", 0),
                    "lines_total": total_data.get("lines", {}).get("total", 0)
                }
        
        # Calcular cobertura global
        backend_coverage = report["backend"].get("total_coverage", 0)
        frontend_coverage = report["frontend"].get("total_coverage", 0)
        
        if backend_coverage > 0 and frontend_coverage > 0:
            report["summary"]["global_coverage"] = (backend_coverage + frontend_coverage) / 2
        elif backend_coverage > 0:
            report["summary"]["global_coverage"] = backend_coverage
        elif frontend_coverage > 0:
            report["summary"]["global_coverage"] = frontend_coverage
        
        # Determinar sucesso geral
        report["summary"]["overall_success"] = (
            report["summary"]["global_coverage"] >= self.coverage_thresholds["global"] and
            report["summary"]["critical_coverage"] >= self.coverage_thresholds["critical_components"]
        )
        
        # Gerar recomendações
        report["recommendations"] = self.generate_recommendations(report)
        
        return report

    def generate_recommendations(self, report: dict) -> list:
        """Gera recomendações baseadas no relatório de cobertura."""
        recommendations = []
        
        # Verificar cobertura global
        global_coverage = report["summary"]["global_coverage"]
        if global_coverage < self.coverage_thresholds["global"]:
            recommendations.append({
                "type": "global_coverage",
                "priority": "high",
                "message": f"Cobertura global ({global_coverage:.1f}%) está abaixo do limite ({self.coverage_thresholds['global']}%)",
                "action": "Adicionar mais testes para aumentar cobertura geral"
            })
        
        # Verificar componentes críticos
        critical_coverage = report["summary"]["critical_coverage"]
        if critical_coverage < self.coverage_thresholds["critical_components"]:
            recommendations.append({
                "type": "critical_coverage",
                "priority": "critical",
                "message": f"Cobertura de componentes críticos ({critical_coverage:.1f}%) está abaixo do limite ({self.coverage_thresholds['critical_components']}%)",
                "action": "Implementar testes para atingir 100% de cobertura nos componentes críticos"
            })
        
        # Verificar componentes específicos
        for component, data in report.get("critical_components", {}).get("components", {}).items():
            if not data.get("meets_requirement", False):
                recommendations.append({
                    "type": "component_coverage",
                    "priority": "high",
                    "component": component,
                    "message": f"Componente {component} tem cobertura de {data.get('coverage', 0):.1f}%",
                    "action": f"Adicionar {data.get('missing_lines', 0)} linhas de teste para {component}"
                })
        
        return recommendations

    def save_report(self, report: dict) -> str:
        """Salva relatório em arquivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_path / f"coverage_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Também salvar como latest
        latest_file = self.reports_path / "coverage_report_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(report_file)

    def print_summary(self, report: dict):
        """Imprime resumo do relatório."""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE COBERTURA DE TESTES - MEDAI")
        print("="*60)
        
        summary = report["summary"]
        
        # Status geral
        status_icon = "✅" if summary["overall_success"] else "❌"
        print(f"\n{status_icon} Status Geral: {'APROVADO' if summary['overall_success'] else 'REPROVADO'}")
        
        # Cobertura global
        global_coverage = summary["global_coverage"]
        global_icon = "✅" if global_coverage >= self.coverage_thresholds["global"] else "❌"
        print(f"{global_icon} Cobertura Global: {global_coverage:.1f}% (Meta: {self.coverage_thresholds['global']}%)")
        
        # Cobertura crítica
        critical_coverage = summary["critical_coverage"]
        critical_icon = "✅" if critical_coverage >= self.coverage_thresholds["critical_components"] else "❌"
        print(f"{critical_icon} Componentes Críticos: {critical_coverage:.1f}% (Meta: {self.coverage_thresholds['critical_components']}%)")
        
        # Backend
        if "backend" in report:
            backend = report["backend"]
            backend_icon = "✅" if backend.get("meets_threshold", False) else "❌"
            print(f"{backend_icon} Backend: {backend.get('total_coverage', 0):.1f}%")
        
        # Frontend
        if "frontend" in report:
            frontend = report["frontend"]
            frontend_icon = "✅" if frontend.get("meets_threshold", False) else "❌"
            print(f"{frontend_icon} Frontend: {frontend.get('total_coverage', 0):.1f}%")
        
        # Componentes críticos detalhados
        if "critical_components" in report and "components" in report["critical_components"]:
            print(f"\n🎯 Componentes Críticos Detalhados:")
            for component, data in report["critical_components"]["components"].items():
                icon = "✅" if data.get("meets_requirement", False) else "❌"
                coverage = data.get("coverage", 0)
                print(f"  {icon} {component}: {coverage:.1f}%")
        
        # Recomendações
        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Recomendações ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:5], 1):  # Mostrar apenas as 5 primeiras
                priority_icon = "🔴" if rec["priority"] == "critical" else "🟡" if rec["priority"] == "high" else "🟢"
                print(f"  {i}. {priority_icon} {rec['message']}")
                print(f"     Ação: {rec['action']}")
        
        print("\n" + "="*60)

    def run_full_analysis(self) -> dict:
        """Executa análise completa de cobertura."""
        print("🚀 Iniciando análise completa de cobertura de testes...")
        
        # Executar análise do backend
        backend_result = self.run_backend_coverage()
        
        # Executar análise do frontend
        frontend_result = self.run_frontend_coverage()
        
        # Gerar relatório consolidado
        report = self.generate_coverage_report(backend_result, frontend_result)
        
        # Salvar relatório
        report_file = self.save_report(report)
        print(f"📄 Relatório salvo em: {report_file}")
        
        # Imprimir resumo
        self.print_summary(report)
        
        return report


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Monitor de Cobertura MedAI")
    parser.add_argument("--project-root", default=".", help="Caminho raiz do projeto")
    parser.add_argument("--backend-only", action="store_true", help="Executar apenas análise do backend")
    parser.add_argument("--frontend-only", action="store_true", help="Executar apenas análise do frontend")
    parser.add_argument("--quiet", action="store_true", help="Modo silencioso")
    
    args = parser.parse_args()
    
    monitor = CoverageMonitor(args.project_root)
    
    try:
        if args.backend_only:
            result = monitor.run_backend_coverage()
            if not args.quiet:
                print("Backend coverage analysis completed")
        elif args.frontend_only:
            result = monitor.run_frontend_coverage()
            if not args.quiet:
                print("Frontend coverage analysis completed")
        else:
            report = monitor.run_full_analysis()
            
            # Exit code baseado no sucesso
            exit_code = 0 if report["summary"]["overall_success"] else 1
            sys.exit(exit_code)
            
    except Exception as e:
        print(f"❌ Erro durante análise de cobertura: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

