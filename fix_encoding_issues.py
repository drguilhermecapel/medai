#!/usr/bin/env python3
"""
Script para corrigir problemas de encoding UTF-8 em arquivos Python
Resolve os erros de SyntaxError: (unicode error) 'utf-8' codec can't decode byte
"""

import os
import chardet
import shutil
from pathlib import Path
from typing import List, Dict, Tuple


class EncodingFixer:
    """Corrige problemas de encoding em arquivos Python"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.problematic_files = []
        self.fixed_files = []
        self.backup_dir = self.project_root / "encoding_backups"
        
    def detect_encoding(self, file_path: Path) -> str:
        """Detecta a codificação de um arquivo"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding'] if result['encoding'] else 'unknown'
        except Exception as e:
            print(f"❌ Erro ao detectar encoding de {file_path}: {e}")
            return 'unknown'
    
    def create_backup(self, file_path: Path) -> Path:
        """Cria backup do arquivo antes de modificar"""
        # Criar diretório de backup se não existir
        self.backup_dir.mkdir(exist_ok=True)
        
        # Criar estrutura de diretórios no backup
        relative_path = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar arquivo
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def fix_file_encoding(self, file_path: Path) -> bool:
        """Corrige encoding de um arquivo específico"""
        try:
            # Detectar encoding atual
            current_encoding = self.detect_encoding(file_path)
            print(f"📄 {file_path}: encoding detectado como {current_encoding}")
            
            if current_encoding == 'utf-8':
                print(f"   ✅ Já está em UTF-8")
                return True
            
            # Criar backup
            backup_path = self.create_backup(file_path)
            print(f"   💾 Backup criado: {backup_path}")
            
            # Ler arquivo com encoding detectado
            with open(file_path, 'r', encoding=current_encoding, errors='replace') as f:
                content = f.read()
            
            # Escrever em UTF-8
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Convertido para UTF-8")
            self.fixed_files.append(str(file_path))
            return True
            
        except Exception as e:
            print(f"   ❌ Erro ao corrigir {file_path}: {e}")
            self.problematic_files.append(str(file_path))
            return False
    
    def scan_python_files(self) -> List[Path]:
        """Encontra todos os arquivos Python no projeto"""
        python_files = []
        
        for file_path in self.project_root.rglob("*.py"):
            # Ignorar arquivos de virtual environment e cache
            if any(part in str(file_path) for part in ['venv', 'env', '__pycache__', '.git']):
                continue
            python_files.append(file_path)
        
        return python_files
    
    def check_utf8_issues(self, file_path: Path) -> List[Tuple[int, str]]:
        """Verifica se um arquivo tem problemas de UTF-8"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        # Tenta decodificar a linha
                        line.encode('utf-8')
                    except UnicodeEncodeError as e:
                        issues.append((line_num, str(e)))
        except UnicodeDecodeError as e:
            issues.append((0, f"Arquivo não pode ser lido como UTF-8: {e}"))
        
        return issues
    
    def fix_specific_problematic_files(self):
        """Corrige os arquivos específicos mencionados no erro do pytest"""
        problematic_files = [
            "app/config.py",
            "app/services/ml_model_service.py", 
            "app/security.py",
            "app/services/validation_service.py"
        ]
        
        print("🔧 Corrigindo arquivos específicos com problemas de encoding...\n")
        
        for file_rel_path in problematic_files:
            file_path = self.project_root / file_rel_path
            
            if file_path.exists():
                print(f"🔍 Verificando {file_path}...")
                
                # Verificar se tem problemas de UTF-8
                issues = self.check_utf8_issues(file_path)
                
                if issues:
                    print(f"   ⚠️  Problemas encontrados: {len(issues)}")
                    for line_num, issue in issues[:3]:  # Mostrar apenas os primeiros 3
                        print(f"      Linha {line_num}: {issue}")
                    
                    # Corrigir encoding
                    self.fix_file_encoding(file_path)
                else:
                    print(f"   ✅ Arquivo OK")
            else:
                print(f"   ❌ Arquivo não encontrado: {file_path}")
            
            print()
    
    def fix_all_python_files(self):
        """Corrige encoding de todos os arquivos Python"""
        print("🔧 Escaneando todos os arquivos Python...\n")
        
        python_files = self.scan_python_files()
        print(f"📁 Encontrados {len(python_files)} arquivos Python")
        print()
        
        for file_path in python_files:
            issues = self.check_utf8_issues(file_path)
            
            if issues:
                print(f"🔍 Corrigindo {file_path}...")
                self.fix_file_encoding(file_path)
            else:
                print(f"✅ {file_path}: OK")
    
    def add_utf8_headers(self):
        """Adiciona headers UTF-8 aos arquivos Python se necessário"""
        python_files = self.scan_python_files()
        
        print("📝 Verificando headers UTF-8...\n")
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Verificar se já tem encoding header
                has_encoding_header = False
                for line in lines[:3]:  # Verificar apenas as primeiras 3 linhas
                    if 'coding:' in line or 'encoding:' in line:
                        has_encoding_header = True
                        break
                
                # Verificar se tem caracteres não-ASCII
                has_non_ascii = False
                content = ''.join(lines)
                try:
                    content.encode('ascii')
                except UnicodeEncodeError:
                    has_non_ascii = True
                
                # Adicionar header se necessário
                if has_non_ascii and not has_encoding_header:
                    print(f"📝 Adicionando header UTF-8 a {file_path}")
                    
                    # Criar backup
                    self.create_backup(file_path)
                    
                    # Adicionar header
                    if lines and lines[0].startswith('#!'):
                        # Se tem shebang, adicionar após
                        lines.insert(1, '# -*- coding: utf-8 -*-\n')
                    else:
                        # Adicionar no início
                        lines.insert(0, '# -*- coding: utf-8 -*-\n')
                    
                    # Salvar arquivo
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    self.fixed_files.append(str(file_path))
                
            except Exception as e:
                print(f"❌ Erro ao processar {file_path}: {e}")
    
    def run_comprehensive_fix(self):
        """Executa correção completa de encoding"""
        print("🚀 INICIANDO CORREÇÃO COMPLETA DE ENCODING\n")
        print("=" * 60)
        
        # 1. Corrigir arquivos específicos problemáticos
        self.fix_specific_problematic_files()
        
        print("=" * 60)
        
        # 2. Verificar e corrigir todos os arquivos Python
        self.fix_all_python_files()
        
        print("=" * 60)
        
        # 3. Adicionar headers UTF-8 onde necessário
        self.add_utf8_headers()
        
        print("=" * 60)
        
        # Relatório final
        print("\n📊 RELATÓRIO FINAL:")
        print(f"✅ Arquivos corrigidos: {len(self.fixed_files)}")
        print(f"❌ Arquivos com problemas: {len(self.problematic_files)}")
        
        if self.fixed_files:
            print("\n📝 Arquivos corrigidos:")
            for file_path in self.fixed_files:
                print(f"   • {file_path}")
        
        if self.problematic_files:
            print("\n⚠️  Arquivos com problemas:")
            for file_path in self.problematic_files:
                print(f"   • {file_path}")
        
        print(f"\n💾 Backups salvos em: {self.backup_dir}")
        print("\n🎯 Agora execute os testes novamente:")
        print("python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Corrige problemas de encoding UTF-8 em arquivos Python")
    parser.add_argument("--project-root", default=".", help="Diretório raiz do projeto")
    parser.add_argument("--specific-only", action="store_true", help="Corrigir apenas arquivos específicos problemáticos")
    
    args = parser.parse_args()
    
    fixer = EncodingFixer(args.project_root)
    
    if args.specific_only:
        fixer.fix_specific_problematic_files()
    else:
        fixer.run_comprehensive_fix()


if __name__ == "__main__":
    main()