#!/bin/bash

# Simple security check script for MEDAI
# This script checks for common security issues without requiring external services

echo "🔐 MEDAI Security Check Report"
echo "============================="
echo ""

# Check for common security patterns in code
echo "📋 Checking for security patterns..."

# Check for hardcoded secrets
echo "🔍 Checking for hardcoded secrets..."
SECRETS_FOUND=0

# Check for potential API keys, passwords, tokens
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" \) \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./.venv/*" \
  -not -path "./backend/.venv/*" \
  -not -path "./.pytest_cache/*" \
  -exec grep -l -i -E "(password\s*=\s*['\"][^'\"]*['\"]|api_key\s*=\s*['\"][^'\"]*['\"]|secret\s*=\s*['\"][^'\"]*['\"]|token\s*=\s*['\"][^'\"]*['\"])" {} \;

if [ $? -eq 0 ]; then
  echo "⚠️  Potential hardcoded secrets found"
  SECRETS_FOUND=1
else
  echo "✅ No obvious hardcoded secrets found"
fi

# Check for SQL injection patterns
echo ""
echo "🔍 Checking for potential SQL injection patterns..."
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" \) \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./.venv/*" \
  -not -path "./backend/.venv/*" \
  -exec grep -l -E "(\+.*['\"].*SELECT|f['\"].*SELECT.*\{|format.*SELECT)" {} \; | head -5

if [ $? -eq 0 ]; then
  echo "⚠️  Potential SQL injection patterns found"
else
  echo "✅ No obvious SQL injection patterns found"
fi

# Check dependencies for known patterns
echo ""
echo "📦 Checking dependencies..."

# Check Python dependencies for common vulnerabilities
if [ -f "backend/requirements.txt" ]; then
  echo "🐍 Python dependencies in requirements.txt:"
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ $line == *"cryptography"* ]]; then
      echo "  ✅ cryptography found (good for security)"
    fi
    if [[ $line == *"django"* && $line == *"<"*"2.2"* ]]; then
      echo "  ⚠️  Django version may be outdated"
    fi
    if [[ $line == *"flask"* && $line == *"<"*"1.1"* ]]; then
      echo "  ⚠️  Flask version may be outdated"
    fi
  done < "backend/requirements.txt"
fi

# Check Node.js dependencies
if [ -f "frontend/package.json" ]; then
  echo ""
  echo "📦 Node.js dependencies:"
  if grep -q '"vite".*"[^5-9]' frontend/package.json; then
    echo "  ⚠️  Vite version may be outdated (check for security updates)"
  else
    echo "  ✅ Vite version appears recent"
  fi
  
  if grep -q '"react".*"1[0-6]' frontend/package.json; then
    echo "  ⚠️  React version may be outdated"
  else
    echo "  ✅ React version appears recent"
  fi
fi

# Check configuration files
echo ""
echo "⚙️  Checking configuration security..."

# Check for debug mode in production
if grep -r -i "debug.*true" --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.venv . >/dev/null 2>&1; then
  echo "⚠️  Debug mode may be enabled in some files"
else
  echo "✅ No obvious debug mode issues found"
fi

# Check for CORS configuration
if grep -r -i "cors.*\*" --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.venv . >/dev/null 2>&1; then
  echo "⚠️  Wildcard CORS configuration found (may be insecure)"
else
  echo "✅ No wildcard CORS configuration found"
fi

# Summary
echo ""
echo "📊 Security Check Summary"
echo "========================"

if [ $SECRETS_FOUND -eq 0 ]; then
  echo "🟢 Overall Status: GOOD"
  echo "✅ No critical security issues detected"
  echo "✅ Basic security practices seem to be followed"
else
  echo "🟡 Overall Status: NEEDS ATTENTION"
  echo "⚠️  Some potential security issues found"
  echo "📋 Review the warnings above and address them"
fi

echo ""
echo "📌 Recommendations:"
echo "  - Use environment variables for sensitive data"
echo "  - Regularly update dependencies"
echo "  - Use HTTPS in production"
echo "  - Implement proper authentication and authorization"
echo "  - Use parameterized queries for database operations"
echo "  - Enable security headers in production"

echo ""
echo "✅ Security check completed!"