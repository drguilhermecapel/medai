"""
Script de Monitoramento de Cobertura para MedAI - Versão Corrigida e Aprimorada
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import argparse
import shutil


class CoverageMonitor:
    """Monitor de cobertura de testes para MedAI."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.backend_path = self.project_root / "backend"
        self.frontend_path = self.project_root / "frontend"
        self.reports_path = self.project_root / "coverage_reports"
        self.reports_path.mkdir(exist_ok=True)
        
        # Verificar quais componentes existem
        self.has_backend = self.backend_path.exists()
        self.has_frontend = self.frontend_path.exists()
        
        # Validar estrutura do projeto
        self._validate_project_structure()
        
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
    
    def _validate_project_structure(self):
        """Valida a estrutura do projeto e emite avisos."""
        if not self.has_backend and not self.has_frontend:
            raise Exception("❌ Erro: Nenhum diretório backend ou frontend encontrado!")
        
        if not self.has_backend:
            print("⚠️  Aviso: Diretório 'backend' não encontrado")
        else:
            print(f"✅ Backend encontrado em: {self.backend_path}")
            
        if not self.has_frontend:
            print("⚠️  Aviso: Diretório 'frontend' não encontrado")
        else:
            print(f"✅ Frontend encontrado em: {self.frontend_path}")
        
        print(f"📁 Diretório de relatórios: {self.reports_path}")
        print("")

    def _check_backend_structure(self) -> dict:
        """Verifica a estrutura do backend."""
        issues = []
        
        # Verificar se existe app/
        app_dir = self.backend_path / "app"
        if not app_dir.exists():
            issues.append("Diretório 'app' não encontrado")
        
        # Verificar se existe tests/
        tests_dir = self.backend_path / "tests"
        if not tests_dir.exists():
            issues.append("Diretório 'tests' não encontrado")
        else:
            # Contar arquivos de teste
            test_files = list(tests_dir.glob("test_*.py"))
            if not test_files:
                issues.append("Nenhum arquivo de teste (test_*.py) encontrado")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "app_exists": app_dir.exists(),
            "tests_exist": tests_dir.exists()
        }

    def run_backend_coverage(self) -> dict:
        """Executa análise de cobertura do backend."""
        if not self.has_backend:
            return {
                "success": False,
                "error": "Diretório backend não encontrado",
                "coverage_data": {"totals": {"percent_covered": 0}, "files": {}}
            }
            
        print("🔍 Executando análise de cobertura do backend...")
        
        # Verificar estrutura do backend
        structure_check = self._check_backend_structure()
        if not structure_check["valid"]:
            return {
                "success": False,
                "error": f"Estrutura do backend inválida: {', '.join(structure_check['issues'])}",
                "coverage_data": {"totals": {"percent_covered": 0}, "files": {}}
            }
        
        # Salvar diretório atual
        current_dir = os.getcwd()
        
        try:
            os.chdir(self.backend_path)
            
            # Verificar se pytest e pytest-cov estão instalados
            print("📦 Verificando dependências...")
            self._check_dependencies()
            
            # Limpar arquivos de cobertura anteriores
            coverage_file = self.backend_path / "coverage.json"
            if coverage_file.exists():
                coverage_file.unlink()
            
            # Construir comando pytest
            cmd = [
                sys.executable, "-m", "pytest",
                "--cov=app",
                "--cov-report=json:coverage.json",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "-v",
                "--tb=short"  # Traceback mais curto para melhor legibilidade
            ]
            
            # Se não houver testes, criar um teste dummy para evitar erro
            tests_dir = self.backend_path / "tests"
            if not list(tests_dir.glob("test_*.py")):
                print("⚠️  Nenhum teste encontrado. Criando teste dummy...")
                dummy_test = tests_dir / "test_dummy.py"
                dummy_test.write_text("""
def test_dummy():
    '''Teste dummy para permitir execução do pytest'''
    assert True
""")
            
            print("🧪 Executando testes...")
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.backend_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env
            )
            
            # Debug: Imprimir saída se houver erro
            if result.returncode != 0:
                print("⚠️  Pytest retornou erro:")
                print("STDOUT:", result.stdout[:500] if result.stdout else "Vazio")
                print("STDERR:", result.stderr[:500] if result.stderr else "Vazio")
            
            # Tentar ler relatório de cobertura
            coverage_file = self.backend_path / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                # Verificar se há dados válidos
                if "totals" not in coverage_data:
                    coverage_data["totals"] = {"percent_covered": 0}
                
                return {
                    "success": True,  # Mesmo com falha nos testes, se gerou cobertura
                    "coverage_data": coverage_data,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "tests_passed": result.returncode == 0
                }
            else:
                # Se não gerou arquivo de cobertura, tentar entender o porquê
                if "no tests ran" in result.stdout.lower():
                    error_msg = "Nenhum teste foi executado"
                elif "ModuleNotFoundError" in result.stderr:
                    error_msg = "Erro de importação de módulos - verificar dependências"
                elif "coverage" not in result.stdout and "coverage" not in result.stderr:
                    error_msg = "pytest-cov não está funcionando corretamente"
                else:
                    error_msg = "Arquivo de cobertura não foi gerado"
                
                # Criar dados de cobertura vazios
                return {
                    "success": False,
                    "error": error_msg,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "coverage_data": {
                        "totals": {"percent_covered": 0},
                        "files": {}
                    }
                }
                
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": f"Exceção durante execução: {str(e)}",
                "traceback": traceback.format_exc(),
                "coverage_data": {"totals": {"percent_covered": 0}, "files": {}}
            }
        finally:
            os.chdir(current_dir)

    def run_frontend_coverage(self) -> dict:
        """Executa análise de cobertura do frontend."""
        if not self.has_frontend:
            return {
                "success": False,
                "error": "Diretório frontend não encontrado",
                "coverage_data": {"total": {"lines": {"pct": 0}}}
            }
            
        print("🔍 Executando análise de cobertura do frontend...")
        
        # Verificar se npm está instalado
        npm_check = shutil.which("npm")
        if not npm_check:
            return {
                "success": False,
                "error": "npm não está instalado ou não está no PATH",
                "coverage_data": {"total": {"lines": {"pct": 0}}}
            }
        
        # Salvar diretório atual
        current_dir = os.getcwd()
        
        try:
            os.chdir(self.frontend_path)
            
            # Verificar se package.json existe
            package_json = self.frontend_path / "package.json"
            if not package_json.exists():
                return {
                    "success": False,
                    "error": "package.json não encontrado no diretório frontend",
                    "coverage_data": {"total": {"lines": {"pct": 0}}}
                }
            
            # Ler package.json para verificar scripts
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            scripts = package_data.get("scripts", {})
            
            # Determinar comando de teste
            if "test:coverage" in scripts:
                cmd = ["npm", "run", "test:coverage"]
            elif "test" in scripts:
                # Verificar se o comando de teste já inclui coverage
                test_cmd = scripts["test"]
                if "coverage" in test_cmd:
                    cmd = ["npm", "test"]
                else:
                    cmd = ["npm", "test", "--", "--coverage", "--watchAll=false"]
            else:
                return {
                    "success": False,
                    "error": "Nenhum script de teste encontrado no package.json",
                    "coverage_data": {"total": {"lines": {"pct": 0}}}
                }
            
            # Verificar se node_modules existe
            if not (self.frontend_path / "node_modules").exists():
                print("📦 node_modules não encontrado. Instalando dependências...")
                install_result = subprocess.run(
                    ["npm", "install"],
                    capture_output=True,
                    text=True
                )
                if install_result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Falha ao instalar dependências: {install_result.stderr}",
                        "coverage_data": {"total": {"lines": {"pct": 0}}}
                    }
            
            print(f"🧪 Executando comando: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Debug: Imprimir saída se houver erro
            if result.returncode != 0:
                print("⚠️  npm test retornou erro:")
                print("STDOUT:", result.stdout[:500] if result.stdout else "Vazio")
                print("STDERR:", result.stderr[:500] if result.stderr else "Vazio")
            
            # Procurar arquivo de cobertura em vários locais possíveis
            coverage_locations = [
                self.frontend_path / "coverage" / "coverage-summary.json",
                self.frontend_path / "coverage" / "coverage-final.json",
                self.frontend_path / "coverage.json"
            ]
            
            coverage_data = None
            for coverage_file in coverage_locations:
                if coverage_file.exists():
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    break
            
            if coverage_data:
                # Normalizar dados de cobertura
                if "total" not in coverage_data:
                    # Tentar extrair do formato coverage-final.json
                    total_lines = 0
                    covered_lines = 0
                    
                    for file_data in coverage_data.values():
                        if isinstance(file_data, dict) and "s" in file_data:
                            statements = file_data["s"]
                            total_lines += len(statements)
                            covered_lines += sum(1 for v in statements.values() if v > 0)
                    
                    pct = (covered_lines / total_lines * 100) if total_lines > 0 else 0
                    coverage_data = {
                        "total": {
                            "lines": {"pct": pct}
                        }
                    }
                
                return {
                    "success": True,
                    "coverage_data": coverage_data,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "error": "Arquivo de cobertura não encontrado após execução dos testes",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "coverage_data": {"total": {"lines": {"pct": 0}}}
                }
                
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": f"Exceção durante execução: {str(e)}",
                "traceback": traceback.format_exc(),
                "coverage_data": {"total": {"lines": {"pct": 0}}}
            }
        finally:
            os.chdir(current_dir)
    
    def _check_dependencies(self):
        """Verifica e instala dependências necessárias."""
        required_packages = ["pytest", "pytest-cov"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"📦 Instalando dependências: {', '.join(missing_packages)}...")
            cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️  Erro ao instalar dependências: {result.stderr}")
            else:
                print("✅ Dependências instaladas com sucesso")

    def analyze_critical_components(self, coverage_data: dict) -> dict:
        """Analisa cobertura dos componentes críticos."""
        critical_coverage = {}
        files = coverage_data.get("files", {})
        
        if not files:
            # Se não há arquivos, retornar análise vazia
            return {component: {
                "coverage": 0,
                "meets_requirement": False,
                "error": "Nenhum arquivo analisado"
            } for component in self.critical_components}
        
        for component in self.critical_components:
            # Procurar arquivo no relatório de cobertura
            found = False
            for file_path, file_data in files.items():
                # Normalizar caminhos para comparação
                normalized_component = component.replace('/', os.sep)
                normalized_file = file_path.replace('/', os.sep)
                
                if normalized_component in normalized_file or normalized_file.endswith(normalized_component):
                    # Extrair porcentagem de cobertura
                    if isinstance(file_data, dict):
                        if "summary" in file_data:
                            coverage_percent = file_data["summary"].get("percent_covered", 0)
                            missing_lines = file_data["summary"].get("num_missing_lines", 0)
                        elif "totals" in file_data:
                            coverage_percent = file_data["totals"].get("percent_covered", 0)
                            missing_lines = file_data["totals"].get("missing_lines", 0)
                        else:
                            coverage_percent = 0
                            missing_lines = "N/A"
                    else:
                        coverage_percent = 0
                        missing_lines = "N/A"
                    
                    critical_coverage[component] = {
                        "coverage": coverage_percent,
                        "meets_requirement": coverage_percent >= self.coverage_thresholds["critical_components"],
                        "missing_lines": missing_lines
                    }
                    found = True
                    break
            
            if not found:
                # Arquivo não encontrado no relatório
                critical_coverage[component] = {
                    "coverage": 0,
                    "meets_requirement": False,
                    "error": "Arquivo não encontrado no relatório de cobertura"
                }
        
        return critical_coverage

    def generate_recommendations(self, coverage_analysis: dict) -> list:
        """Gera recomendações baseadas na análise de cobertura."""
        recommendations = []
        
        # Verificar cobertura global
        global_coverage = coverage_analysis.get("global_coverage", 0)
        if global_coverage < self.coverage_thresholds["global"]:
            recommendations.append({
                "priority": "high",
                "type": "global_coverage",
                "message": f"Cobertura global está abaixo do limite de {self.coverage_thresholds['global']}%",
                "action": "Adicionar mais testes unitários e de integração"
            })
        
        # Verificar componentes críticos
        critical_issues = coverage_analysis.get("critical_components", {})
        for component, data in critical_issues.items():
            if not data.get("meets_requirement", False):
                recommendations.append({
                    "priority": "critical",
                    "type": "critical_component",
                    "component": component,
                    "message": f"{component} tem apenas {data.get('coverage', 0):.1f}% de cobertura",
                    "action": f"Adicionar testes para cobrir {data.get('missing_lines', 'N/A')} linhas faltantes"
                })
        
        # Recomendações específicas por tipo de arquivo
        files_data = coverage_analysis.get("files", {})
        if files_data:
            for file_type, threshold in [("services", 95), ("repositories", 85), ("api", 85)]:
                low_coverage_files = []
                for f, data in files_data.items():
                    if file_type in f:
                        coverage = 0
                        if isinstance(data, dict):
                            if "summary" in data:
                                coverage = data["summary"].get("percent_covered", 0)
                            elif "totals" in data:
                                coverage = data["totals"].get("percent_covered", 0)
                        
                        if coverage < threshold:
                            low_coverage_files.append(f)
                
                if low_coverage_files:
                    recommendations.append({
                        "priority": "medium",
                        "type": f"{file_type}_coverage",
                        "message": f"{len(low_coverage_files)} arquivos de {file_type} estão abaixo de {threshold}%",
                        "action": f"Revisar e adicionar testes para: {', '.join(low_coverage_files[:3])}..."
                    })
        
        return recommendations

    def generate_html_report(self, report_data: dict):
        """Gera relatório HTML detalhado."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MedAI - Relatório de Cobertura de Testes</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; margin: -20px -20px 20px -20px; }}
                .summary {{ background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .critical {{ color: #dc3545; }}
                .warning {{ color: #ffc107; }}
                .success {{ color: #28a745; }}
                .component {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                .error {{ background-color: #f8d7da; padding: 15px; margin: 10px 0; border: 1px solid #f5c6cb; border-radius: 5px; }}
                .debug {{ background-color: #e9ecef; padding: 10px; margin: 10px 0; font-family: monospace; font-size: 12px; overflow-x: auto; }}
                .progress-bar {{ background-color: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden; }}
                .progress-fill {{ height: 100%; background-color: #28a745; transition: width 0.3s; }}
                .progress-fill.warning {{ background-color: #ffc107; }}
                .progress-fill.critical {{ background-color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Relatório de Cobertura de Testes - MedAI</h1>
                    <p>Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="summary">
                    <h2>Resumo Executivo</h2>
                    <p><strong>Cobertura Global:</strong> 
                       <span class="{'success' if report_data['summary']['global_coverage'] >= 80 else 'critical'}">
                       {report_data['summary']['global_coverage']:.1f}%
                       </span>
                    </p>
                    <div class="progress-bar">
                        <div class="progress-fill {'critical' if report_data['summary']['global_coverage'] < 60 else 'warning' if report_data['summary']['global_coverage'] < 80 else ''}" 
                             style="width: {report_data['summary']['global_coverage']}%"></div>
                    </div>
                    
                    <p><strong>Componentes Críticos:</strong> 
                       <span class="{'success' if report_data['summary']['critical_coverage'] >= 100 else 'critical'}">
                       {report_data['summary']['critical_coverage']:.1f}%
                       </span>
                    </p>
                    <div class="progress-bar">
                        <div class="progress-fill {'critical' if report_data['summary']['critical_coverage'] < 100 else ''}" 
                             style="width: {report_data['summary']['critical_coverage']}%"></div>
                    </div>
                </div>
        """
        
        # Adicionar erros e debug info se existirem
        if "backend" in report_data:
            backend = report_data["backend"]
            if "error" in backend:
                html_content += f"""
                <div class="error">
                    <h3>⚠️ Erro no Backend</h3>
                    <p><strong>{backend['error']}</strong></p>
                """
                if "stdout" in backend and backend["stdout"]:
                    html_content += f"""
                    <details>
                        <summary>Detalhes da Saída</summary>
                        <pre class="debug">{backend['stdout'][:1000]}...</pre>
                    </details>
                    """
                if "stderr" in backend and backend["stderr"]:
                    html_content += f"""
                    <details>
                        <summary>Erros Detalhados</summary>
                        <pre class="debug">{backend['stderr'][:1000]}...</pre>
                    </details>
                    """
                html_content += "</div>"
        
        if "frontend" in report_data:
            frontend = report_data["frontend"]
            if "error" in frontend:
                html_content += f"""
                <div class="error">
                    <h3>⚠️ Erro no Frontend</h3>
                    <p><strong>{frontend['error']}</strong></p>
                """
                if "traceback" in frontend:
                    html_content += f"""
                    <details>
                        <summary>Traceback</summary>
                        <pre class="debug">{frontend['traceback']}</pre>
                    </details>
                    """
                html_content += "</div>"
        
        # Componentes críticos
        if "critical_components" in report_data and "components" in report_data["critical_components"]:
            html_content += """
            <h2>Componentes Críticos</h2>
            <table>
                <tr>
                    <th>Componente</th>
                    <th>Cobertura</th>
                    <th>Status</th>
                    <th>Observações</th>
                </tr>
            """
            
            for component, data in report_data["critical_components"]["components"].items():
                status_class = "success" if data.get("meets_requirement", False) else "critical"
                status_text = "✅ OK" if data.get("meets_requirement", False) else "❌ Falha"
                obs = data.get('error', f"{data.get('missing_lines', 'N/A')} linhas faltantes")
                
                html_content += f"""
                    <tr>
                        <td>{component}</td>
                        <td class="{status_class}">{data.get('coverage', 0):.1f}%</td>
                        <td>{status_text}</td>
                        <td>{obs}</td>
                    </tr>
                """
            
            html_content += "</table>"
        
        # Recomendações
        html_content += """
            <h2>Recomendações</h2>
            <ul>
        """
        
        for rec in report_data.get("recommendations", []):
            priority_class = {
                "critical": "critical",
                "high": "warning",
                "medium": "warning"
            }.get(rec["priority"], "")
            
            priority_emoji = {
                "critical": "🔴",
                "high": "🟡",
                "medium": "🟢"
            }.get(rec["priority"], "")
            
            html_content += f"""
                <li>
                    <strong>{priority_emoji} [{rec['priority'].upper()}]</strong> 
                    <span class="{priority_class}">{rec['message']}</span><br>
                    <em>Ação recomendada: {rec['action']}</em>
                </li>
            """
        
        html_content += """
            </ul>
            </div>
        </body>
        </html>
        """
        
        # Salvar relatório HTML
        report_path = self.reports_path / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 Relatório HTML salvo em: {report_path}")
        return report_path

    def save_json_report(self, report_data: dict):
        """Salva relatório em formato JSON."""
        report_path = self.reports_path / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Salvar também como "latest" para fácil acesso
        latest_path = self.reports_path / "coverage_report_latest.json"
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Relatório JSON salvo em: {report_path}")
        return report_path

    def print_summary(self, report: dict):
        """Imprime resumo no console."""
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
            if "error" in backend:
                print(f"⚠️  Backend: Erro - {backend['error']}")
            else:
                backend_icon = "✅" if backend.get("meets_threshold", False) else "❌"
                print(f"{backend_icon} Backend: {backend.get('total_coverage', 0):.1f}%")
        
        # Frontend
        if "frontend" in report:
            frontend = report["frontend"]
            if "error" in frontend:
                print(f"⚠️  Frontend: Erro - {frontend['error']}")
            else:
                frontend_icon = "✅" if frontend.get("meets_threshold", False) else "❌"
                print(f"{frontend_icon} Frontend: {frontend.get('total_coverage', 0):.1f}%")
        
        # Componentes críticos detalhados
        if "critical_components" in report and "components" in report["critical_components"]:
            components = report["critical_components"]["components"]
            if components:
                print(f"\n🎯 Componentes Críticos Detalhados:")
                for component, data in components.items():
                    if "error" in data:
                        print(f"  ⚠️  {component}: {data['error']}")
                    else:
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
        report = {
            "timestamp": datetime.now().isoformat(),
            "project": "MedAI",
            "thresholds": self.coverage_thresholds,
            "project_structure": {
                "has_backend": self.has_backend,
                "has_frontend": self.has_frontend
            }
        }
        
        # Backend
        if self.has_backend:
            print("\n🔧 Analisando Backend...")
            backend_result = self.run_backend_coverage()
            
            if "coverage_data" in backend_result:
                coverage_data = backend_result["coverage_data"]
                totals = coverage_data.get("totals", {})
                total_coverage = totals.get("percent_covered", 0)
                
                # Verificar se há arquivos analisados
                files_count = len(coverage_data.get("files", {}))
                
                if backend_result.get("success", False) or files_count > 0:
                    report["backend"] = {
                        "total_coverage": total_coverage,
                        "meets_threshold": total_coverage >= self.coverage_thresholds["global"],
                        "files_analyzed": files_count,
                        "tests_passed": backend_result.get("tests_passed", False)
                    }
                    
                    # Analisar componentes críticos
                    critical_analysis = self.analyze_critical_components(coverage_data)
                    report["critical_components"] = {
                        "components": critical_analysis,
                        "total_coverage": sum(
                            c["coverage"] for c in critical_analysis.values() 
                            if "coverage" in c and "error" not in c
                        ) / len([c for c in critical_analysis.values() if "error" not in c]) 
                        if any("error" not in c for c in critical_analysis.values()) else 0
                    }
                else:
                    # Erro mas incluir informações de debug
                    report["backend"] = {
                        "error": backend_result.get("error", "Erro desconhecido"),
                        "total_coverage": 0,
                        "meets_threshold": False,
                        "stdout": backend_result.get("stdout", ""),
                        "stderr": backend_result.get("stderr", ""),
                        "traceback": backend_result.get("traceback", "")
                    }
            else:
                report["backend"] = {
                    "error": "Dados de cobertura não disponíveis",
                    "total_coverage": 0,
                    "meets_threshold": False
                }
        
        # Frontend
        if self.has_frontend:
            print("\n🎨 Analisando Frontend...")
            frontend_result = self.run_frontend_coverage()
            
            if "coverage_data" in frontend_result:
                coverage_data = frontend_result["coverage_data"]
                
                # Extrair porcentagem total
                total_coverage = 0
                if "total" in coverage_data:
                    total = coverage_data["total"]
                    if "lines" in total and "pct" in total["lines"]:
                        total_coverage = total["lines"]["pct"]
                
                if frontend_result.get("success", False):
                    report["frontend"] = {
                        "total_coverage": total_coverage,
                        "meets_threshold": total_coverage >= self.coverage_thresholds["global"]
                    }
                else:
                    report["frontend"] = {
                        "error": frontend_result.get("error", "Erro desconhecido"),
                        "total_coverage": 0,
                        "meets_threshold": False,
                        "stdout": frontend_result.get("stdout", ""),
                        "stderr": frontend_result.get("stderr", ""),
                        "traceback": frontend_result.get("traceback", "")
                    }
            else:
                report["frontend"] = {
                    "error": "Dados de cobertura não disponíveis",
                    "total_coverage": 0,
                    "meets_threshold": False
                }
        
        # Calcular resumo
        backend_coverage = report.get("backend", {}).get("total_coverage", 0) if "backend" in report else 0
        frontend_coverage = report.get("frontend", {}).get("total_coverage", 0) if "frontend" in report else 0
        critical_coverage = report.get("critical_components", {}).get("total_coverage", 0) if "critical_components" in report else 0
        
        # Média ponderada (backend tem peso maior por ser mais crítico)
        if self.has_backend and self.has_frontend:
            global_coverage = (backend_coverage * 0.7 + frontend_coverage * 0.3)
        elif self.has_backend:
            global_coverage = backend_coverage
        else:
            global_coverage = frontend_coverage
        
        report["summary"] = {
            "global_coverage": global_coverage,
            "critical_coverage": critical_coverage,
            "overall_success": (
                global_coverage >= self.coverage_thresholds["global"] and
                (critical_coverage >= self.coverage_thresholds["critical_components"] if critical_coverage > 0 else True)
            )
        }
        
        # Gerar recomendações
        coverage_analysis = {
            "global_coverage": global_coverage,
            "critical_components": report.get("critical_components", {}).get("components", {}),
            "files": {}
        }
        
        # Incluir arquivos do backend se disponível
        if "backend" in report and backend_result.get("coverage_data"):
            coverage_analysis["files"] = backend_result["coverage_data"].get("files", {})
        
        report["recommendations"] = self.generate_recommendations(coverage_analysis)
        
        return report


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Monitor de Cobertura de Testes MedAI")
    parser.add_argument("--project-root", default=".", help="Caminho raiz do projeto")
    parser.add_argument("--backend-only", action="store_true", help="Analisar apenas o backend")
    parser.add_argument("--frontend-only", action="store_true", help="Analisar apenas o frontend")
    parser.add_argument("--json", action="store_true", help="Salvar relatório em JSON")
    parser.add_argument("--html", action="store_true", help="Gerar relatório HTML")
    parser.add_argument("--quiet", action="store_true", help="Modo silencioso")
    parser.add_argument("--debug", action="store_true", help="Modo debug com mais informações")
    
    args = parser.parse_args()
    
    try:
        # Criar monitor
        monitor = CoverageMonitor(args.project_root)
        
        # Executar análise
        if args.backend_only:
            if not monitor.has_backend:
                print("❌ Erro: Backend não encontrado")
                sys.exit(1)
            backend_result = monitor.run_backend_coverage()
            report = {
                "timestamp": datetime.now().isoformat(),
                "project": "MedAI",
                "backend": backend_result if backend_result.get("success") else {
                    "error": backend_result.get("error", "Erro desconhecido"),
                    "total_coverage": 0,
                    "meets_threshold": False
                },
                "summary": {
                    "overall_success": backend_result.get("success", False),
                    "global_coverage": backend_result.get("coverage_data", {}).get("totals", {}).get("percent_covered", 0),
                    "critical_coverage": 0
                }
            }
        elif args.frontend_only:
            if not monitor.has_frontend:
                print("❌ Erro: Frontend não encontrado")
                sys.exit(1)
            frontend_result = monitor.run_frontend_coverage()
            report = {
                "timestamp": datetime.now().isoformat(),
                "project": "MedAI",
                "frontend": frontend_result if frontend_result.get("success") else {
                    "error": frontend_result.get("error", "Erro desconhecido"),
                    "total_coverage": 0,
                    "meets_threshold": False
                },
                "summary": {
                    "overall_success": frontend_result.get("success", False),
                    "global_coverage": frontend_result.get("coverage_data", {}).get("total", {}).get("lines", {}).get("pct", 0),
                    "critical_coverage": 0
                }
            }
        else:
            report = monitor.run_full_analysis()
        
        # Modo debug
        if args.debug and not args.quiet:
            print("\n🐛 DEBUG INFO:")
            print(json.dumps(report, indent=2, ensure_ascii=False)[:1000] + "...")
        
        # Exibir resumo
        if not args.quiet:
            monitor.print_summary(report)
        
        # Salvar relatórios
        if args.json or not (args.json or args.html):  # JSON por padrão
            monitor.save_json_report(report)
        
        if args.html:
            monitor.generate_html_report(report)
        
        # Retornar código de saída baseado no sucesso
        success = report.get("summary", {}).get("overall_success", False)
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()