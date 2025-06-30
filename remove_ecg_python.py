#!/usr/bin/env python3
"""
Script de Limpeza Precisa do ECG - MEDAI
Remove imports, referências e configurações ECG dos arquivos restantes
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def confirm_operation():
    """Confirma a operação com o usuário"""
    print("🚨 AVISO: Esta operação modificará arquivos existentes")
    print("Digite 'CONFIRMO' para continuar ou qualquer outra coisa para cancelar:")
    confirmation = input().strip()
    
    if confirmation != "CONFIRMO":
        print("❌ Operação cancelada pelo usuário")
        exit(1)

def create_report():
    """Cria relatório da operação"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return {
        "timestamp": timestamp,
        "files_modified": [],
        "imports_removed": [],
        "references_removed": [],
        "errors": []
    }

def backup_file(file_path, backup_dir):
    """Faz backup de um arquivo antes de modificá-lo"""
    backup_path = backup_dir / file_path.name
    try:
        backup_path.write_text(file_path.read_text())
        return True
    except Exception as e:
        print(f"⚠️ Erro ao fazer backup de {file_path}: {e}")
        return False

def remove_ecg_imports(file_path, report):
    """Remove imports relacionados ao ECG"""
    try:
        content = file_path.read_text()
        original_content = content
        
        # Padrões de imports ECG
        import_patterns = [
            r'from\s+.*ecg.*\s+import.*\n',
            r'import\s+.*ecg.*\n',
            r'from\s+app\.services\.ecg.*\s+import.*\n',
            r'from\s+app\.models\.ecg.*\s+import.*\n',
            r'from\s+app\.schemas\.ecg.*\s+import.*\n',
            r'from\s+.*\.ecg.*\s+import.*\n']
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                report["imports_removed"].append(f"{file_path}: {match.strip()}")
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Remover linhas vazias extras
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        if content != original_content:
            file_path.write_text(content)
            report["files_modified"].append(str(file_path))
            print(f"✅ Imports ECG removidos de: {file_path}")
            return True
            
    except Exception as e:
        error_msg = f"Erro ao processar {file_path}: {e}"
        report["errors"].append(error_msg)
        print(f"❌ {error_msg}")
        
    return False

def remove_ecg_references(file_path, report):
    """Remove referências ECG do código"""
    try:
        content = file_path.read_text()
        original_content = content
        
        # Padrões de referências ECG
        reference_patterns = [
            r'app\.include_router\(.*ecg.*\)',
            r'router\s*=.*ecg.*',
            r'ECG_[A-Z_]+\s*[:=].*',
            r'ecg_[a-z_]+\s*[:=].*',
            r'[\s]*',
            r"[\s]*",
            r'/ecg["\']',
            r'tags=\["ecg.*"\]',
            r'']
        
        for pattern in reference_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                report["references_removed"].append(f"{file_path}: {match.strip()}")
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Limpar linhas vazias e vírgulas órfãs
        content = re.sub(r',\s*,', ',', content)
        content = re.sub(r'\[\s*,', '[', content)
        content = re.sub(r',\s*\]', ']', content)
        content = re.sub(r'\(\s*,', '(', content)
        content = re.sub(r',\s*\)', ')', content)
        
        if content != original_content:
            file_path.write_text(content)
            if str(file_path) not in report["files_modified"]:
                report["files_modified"].append(str(file_path))
            print(f"✅ Referências ECG removidas de: {file_path}")
            return True
            
    except Exception as e:
        error_msg = f"Erro ao processar referências em {file_path}: {e}"
        report["errors"].append(error_msg)
        print(f"❌ {error_msg}")
        
    return False

def clean_requirements_file(file_path, report):
    """Limpa dependências ECG do requirements.txt"""
    try:
        if not file_path.exists():
            return False
            
        content = file_path.read_text()
        lines = content.split('\n')
        
        # Dependências a remover (se usadas apenas para ECG)
        ecg_dependencies = [
            'scipy',
            'numpy', 
            'matplotlib',
            'seaborn',
            'plotly',
            'scikit-learn',
            'tensorflow',
            'torch',
            'wfdb',
            'neurokit2'
        ]
        
        filtered_lines = []
        for line in lines:
            line_lower = line.lower()
            if any(dep in line_lower for dep in ecg_dependencies):
                print(f"⚠️ Dependência ECG encontrada em {file_path}: {line}")
                print("   Revisar manualmente se é usada apenas para ECG")
                filtered_lines.append(f"# {line}  # Comentado - revisar se usado apenas para ECG")
                report["references_removed"].append(f"{file_path}: {line}")
            else:
                filtered_lines.append(line)
        
        new_content = '\n'.join(filtered_lines)
        if new_content != content:
            file_path.write_text(new_content)
            if str(file_path) not in report["files_modified"]:
                report["files_modified"].append(str(file_path))
            print(f"✅ Requirements limpo: {file_path}")
            return True
            
    except Exception as e:
        error_msg = f"Erro ao limpar requirements {file_path}: {e}"
        report["errors"].append(error_msg)
        print(f"❌ {error_msg}")
        
    return False

def process_directory(directory, report, backup_dir):
    """Processa todos os arquivos de um diretório"""
    print(f"🔄 Processando diretório: {directory}")
    
    # Extensões de arquivo para processar
    extensions = {'.py', '.ts', '.tsx', '.js', '.jsx', '.txt', '.yml', '.yaml'}
    
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix in extensions:
            # Pular arquivos de backup
            if 'backup_ecg' in str(file_path):
                continue
                
            # Fazer backup do arquivo
            backup_file(file_path, backup_dir)
            
            # Processar arquivo
            if file_path.suffix == '.py':
                remove_ecg_imports(file_path, report)
                remove_ecg_references(file_path, report)
            elif file_path.suffix in {'.ts', '.tsx', '.js', '.jsx'}:
                remove_ecg_references(file_path, report)
            elif file_path.name == 'requirements.txt':
                clean_requirements_file(file_path, report)
            elif file_path.suffix in {'.yml', '.yaml'}:
                remove_ecg_references(file_path, report)

def main():
    """Função principal"""
    print("🧹 Script de Limpeza Precisa do ECG - MEDAI")
    print("=" * 50)
    
    confirm_operation()
    
    # Criar diretório de backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backup_ecg_python_{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    
    # Criar relatório
    report = create_report()
    
    # Processar diretórios
    directories_to_process = [
        Path("backend"),
        Path("frontend"),
        Path("."),  # Arquivos na raiz
    ]
    
    for directory in directories_to_process:
        if directory.exists():
            process_directory(directory, report, backup_dir)
    
    # Salvar relatório
    report_file = Path(f"ecg_removal_report_{timestamp}.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DA OPERAÇÃO")
    print("=" * 50)
    print(f"✅ Arquivos modificados: {len(report['files_modified'])}")
    print(f"🗑️ Imports removidos: {len(report['imports_removed'])}")
    print(f"🔗 Referências removidas: {len(report['references_removed'])}")
    print(f"❌ Erros encontrados: {len(report['errors'])}")
    print(f"📁 Backup salvo em: {backup_dir}")
    print(f"📋 Relatório salvo em: {report_file}")
    
    if report['errors']:
        print("\n⚠️ ERROS ENCONTRADOS:")
        for error in report['errors']:
            print(f"   - {error}")
    
    print("\n✅ Limpeza precisa concluída!")
    print("⚠️ Revisar manualmente os arquivos modificados antes de continuar")

if __name__ == "__main__":
    main()

