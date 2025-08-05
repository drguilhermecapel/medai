#!/bin/bash
# Poetry Migration Validation Script

echo "🔍 Testing Poetry Configuration..."

# Check if pyproject.toml exists and is valid
echo "✅ Checking pyproject.toml..."
poetry check

# Test dependency resolution
echo "✅ Testing dependency resolution..."
poetry install --dry-run

# Test if main app can be imported
echo "✅ Testing app import..."
poetry run python -c "from app.main import app; print('✅ FastAPI app imported successfully')"

# Test pytest execution
echo "✅ Testing pytest..."
poetry run pytest tests/test_simple.py -q

# Test development tools
echo "✅ Testing development tools..."
poetry run black --check app/main.py || echo "⚠️  Black formatting needed"
poetry run isort --check-only app/main.py || echo "⚠️  isort formatting needed"
poetry run flake8 app/main.py || echo "⚠️  Flake8 warnings found"

echo "🎉 Poetry migration validation complete!"