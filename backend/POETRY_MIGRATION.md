# Poetry Migration Guide - MedAI Backend

## 🎯 **Migration Summary**

The backend has been successfully migrated from requirements.txt to Poetry for modern dependency management and to resolve critical dependency conflicts.

## 📦 **What Changed**

### **Removed Files:**
- `requirements.txt` (obsolete)
- `app/modules/radiologia/requirements.txt` (duplicated/conflicting)

### **Added Files:**
- `pyproject.toml` - Main configuration file with all dependencies and tool settings
- `poetry.lock` - Lock file ensuring deterministic builds
- `validate_poetry.sh` - Validation script for testing Poetry setup

### **Updated Files:**
- `Dockerfile` - Updated to use Poetry virtual environment

## 🔧 **Dependency Conflicts Resolved**

| Package | Old Version (requirements.txt) | Old Version (radiologia) | New Version (pyproject.toml) |
|---------|-------------------------------|--------------------------|------------------------------|
| pytest | `>=6.2.0` | `>=7.0.0` | `^7.4.0` |
| cryptography | `>=3.4.0` | `>=41.0.0` | `^41.0.0` |
| Pillow | `>=8.3.0` | `>=10.0.0` | `^10.0.0` |

## 🚀 **Developer Commands**

### **Installation:**
```bash
# Install all dependencies
poetry install

# Install only production dependencies
poetry install --only main

# Install with development dependencies
poetry install --with dev
```

### **Running the Application:**
```bash
# Development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run any Python command
poetry run python -m app.main
```

### **Testing:**
```bash
# Run all tests with coverage
poetry run pytest

# Run specific test file
poetry run pytest tests/test_simple.py

# Run tests with verbose output
poetry run pytest -v
```

### **Code Quality:**
```bash
# Format code with Black
poetry run black app tests

# Sort imports with isort
poetry run isort app tests

# Lint with flake8
poetry run flake8 app tests

# Type checking with mypy
poetry run mypy app
```

### **Adding/Removing Dependencies:**
```bash
# Add production dependency
poetry add fastapi

# Add development dependency
poetry add --group dev pytest-mock

# Remove dependency
poetry remove package-name

# Update dependencies
poetry update
```

## 🐳 **Docker**

The Dockerfile has been updated to work with Poetry:
- Uses Poetry virtual environment (`POETRY_VENV_IN_PROJECT=1`)
- Installs only production dependencies in container
- Uses `poetry run` to execute the application

## 📋 **Configuration**

All tool configurations are centralized in `pyproject.toml`:
- **pytest**: Coverage reporting, test discovery, markers
- **black**: Code formatting (88 char line length)
- **isort**: Import sorting (compatible with black)
- **mypy**: Type checking with strict settings
- **coverage**: HTML, XML, and JSON reporting

## ✅ **Validation**

Run the validation script to ensure everything works:
```bash
./validate_poetry.sh
```

This will test:
- pyproject.toml syntax
- Dependency resolution
- App import functionality
- Test execution
- Development tools

## 🎯 **Benefits**

1. **Zero Dependency Conflicts** - All version conflicts resolved
2. **Deterministic Builds** - poetry.lock ensures consistent installs
3. **Modern Tooling** - Poetry provides better dependency resolution
4. **Unified Configuration** - All tools configured in one file
5. **Better CI/CD** - Eliminates the dependency conflicts causing build failures