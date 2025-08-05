#!/usr/bin/env python3
"""
CI/CD Configuration Validator
Validates the CI/CD setup and configuration files
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return Path(filepath).exists()

def validate_yaml(filepath: str) -> Tuple[bool, str]:
    """Validate YAML syntax"""
    try:
        with open(filepath, 'r') as file:
            yaml.safe_load(file)
        return True, "Valid YAML"
    except yaml.YAMLError as e:
        return False, f"YAML Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_json(filepath: str) -> Tuple[bool, str]:
    """Validate JSON syntax"""
    try:
        with open(filepath, 'r') as file:
            json.load(file)
        return True, "Valid JSON"
    except json.JSONDecodeError as e:
        return False, f"JSON Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_workflows() -> List[Dict]:
    """Validate GitHub workflows"""
    workflows_dir = Path(".github/workflows")
    results = []
    
    required_workflows = [
        "ci-enhanced.yml",
        "security.yml", 
        "performance.yml",
        "quality-gates.yml",
        "deploy.yml",
        "release.yml"
    ]
    
    for workflow in required_workflows:
        filepath = workflows_dir / workflow
        exists = filepath.exists()
        
        if exists:
            valid, message = validate_yaml(str(filepath))
            status = "✅" if valid else "❌"
        else:
            valid = False
            message = "File not found"
            status = "❌"
        
        results.append({
            "file": workflow,
            "exists": exists,
            "valid": valid,
            "message": message,
            "status": status
        })
    
    return results

def validate_config_files() -> List[Dict]:
    """Validate configuration files"""
    config_files = [
        (".github/dependabot.yml", "yaml"),
        (".github/codeql/codeql-config.yml", "yaml"),
        (".pre-commit-config.yaml", "yaml"),
        ("frontend/.audit-ci.json", "json"),
        ("frontend/.eslintrc-security.js", "js"),
    ]
    
    results = []
    
    for filepath, file_type in config_files:
        exists = check_file_exists(filepath)
        
        if exists:
            if file_type == "yaml":
                valid, message = validate_yaml(filepath)
            elif file_type == "json":
                valid, message = validate_json(filepath)
            else:
                valid = True
                message = "File exists (syntax not validated)"
            
            status = "✅" if valid else "❌"
        else:
            valid = False
            message = "File not found"
            status = "❌"
        
        results.append({
            "file": filepath,
            "exists": exists,
            "valid": valid,
            "message": message,
            "status": status
        })
    
    return results

def validate_directory_structure() -> List[Dict]:
    """Validate required directory structure"""
    required_dirs = [
        ".github/workflows",
        ".github/codeql",
        "backend",
        "frontend",
        "scripts"
    ]
    
    results = []
    
    for directory in required_dirs:
        exists = Path(directory).is_dir()
        status = "✅" if exists else "❌"
        message = "Directory exists" if exists else "Directory not found"
        
        results.append({
            "directory": directory,
            "exists": exists,
            "status": status,
            "message": message
        })
    
    return results

def check_environment_setup() -> List[Dict]:
    """Check environment setup"""
    checks = [
        ("Git repository", ".git", "dir"),
        ("Environment example", ".env.example", "file"),
        ("GitIgnore", ".gitignore", "file"),
        ("Secrets baseline", ".secrets.baseline", "file"),
        ("Documentation", "ci_cd_improvements.md", "file")
    ]
    
    results = []
    
    for name, path, check_type in checks:
        if check_type == "dir":
            exists = Path(path).is_dir()
        else:
            exists = Path(path).is_file()
        
        status = "✅" if exists else "❌"
        message = f"{check_type.title()} exists" if exists else f"{check_type.title()} not found"
        
        results.append({
            "check": name,
            "path": path,
            "exists": exists,
            "status": status,
            "message": message
        })
    
    return results

def print_results(title: str, results: List[Dict]):
    """Print validation results"""
    print(f"\n{title}")
    print("=" * len(title))
    
    for result in results:
        if "file" in result:
            print(f"{result['status']} {result['file']}")
            if not result['valid']:
                print(f"   ↳ {result['message']}")
        elif "directory" in result:
            print(f"{result['status']} {result['directory']}/")
        elif "check" in result:
            print(f"{result['status']} {result['check']} ({result['path']})")

def main():
    """Main validation function"""
    print("🔍 CI/CD Configuration Validator")
    print("=" * 40)
    
    # Change to repository root if script is run from scripts directory
    if Path.cwd().name == "scripts":
        os.chdir("..")
    
    # Validate directory structure
    dir_results = validate_directory_structure()
    print_results("📁 Directory Structure", dir_results)
    
    # Validate workflows
    workflow_results = validate_workflows()
    print_results("🔄 GitHub Workflows", workflow_results)
    
    # Validate config files
    config_results = validate_config_files()
    print_results("⚙️  Configuration Files", config_results)
    
    # Check environment setup
    env_results = check_environment_setup()
    print_results("🌍 Environment Setup", env_results)
    
    # Summary
    total_checks = len(dir_results) + len(workflow_results) + len(config_results) + len(env_results)
    
    failed_checks = []
    for results in [dir_results, workflow_results, config_results, env_results]:
        for result in results:
            if not result.get('exists', True) or not result.get('valid', True):
                failed_checks.append(result)
    
    passed_checks = total_checks - len(failed_checks)
    
    print(f"\n📊 Summary")
    print("=" * 10)
    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks} ✅")
    print(f"Failed: {len(failed_checks)} ❌")
    
    if failed_checks:
        print(f"\n⚠️  Issues Found:")
        for check in failed_checks:
            if "file" in check:
                print(f"   • {check['file']}: {check['message']}")
            elif "directory" in check:
                print(f"   • {check['directory']}/: {check['message']}")
            elif "check" in check:
                print(f"   • {check['check']}: {check['message']}")
        
        print(f"\n🔧 Next Steps:")
        print("   1. Run the setup script: ./scripts/setup-ci-cd.sh")
        print("   2. Review the CI/CD documentation: ci_cd_improvements.md")
        print("   3. Fix any missing or invalid files")
        
        sys.exit(1)
    else:
        print(f"\n🎉 All checks passed! Your CI/CD setup is ready.")
        print(f"\n🚀 Next Steps:")
        print("   1. Commit your changes")
        print("   2. Push to trigger the CI/CD pipeline")
        print("   3. Review the results in GitHub Actions")

if __name__ == "__main__":
    main()