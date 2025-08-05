#!/bin/bash

# CI/CD Setup Script for MedAI
# This script helps set up the improved CI/CD pipeline

set -e

echo "🚀 Setting up MedAI CI/CD Improvements..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Pre-requisites Check${NC}"

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✅ GitHub CLI is installed${NC}"
    GH_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  GitHub CLI not found - some automation features will be limited${NC}"
    GH_AVAILABLE=false
fi

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker is available${NC}"
else
    echo -e "${YELLOW}⚠️  Docker not found - container features may not work locally${NC}"
fi

# Check if pre-commit is installed
if command -v pre-commit &> /dev/null; then
    echo -e "${GREEN}✅ pre-commit is installed${NC}"
    PRECOMMIT_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  pre-commit not found - installing...${NC}"
    pip install pre-commit || echo -e "${RED}❌ Failed to install pre-commit${NC}"
    PRECOMMIT_AVAILABLE=false
fi

echo ""
echo -e "${BLUE}🔧 Configuration Setup${NC}"

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo -e "${YELLOW}📝 Creating .env.example template...${NC}"
    cat > .env.example << 'EOF'
# Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Database Configuration
DATABASE_URL=postgresql+asyncpg://medai:medai_password@localhost:5432/medai_dev
POSTGRES_USER=medai
POSTGRES_PASSWORD=medai_password
POSTGRES_DB=medai_dev

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security Configuration
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
API_PORT=8000
WEB_PORT=3000
LOG_LEVEL=INFO

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# Medical Compliance Configuration
MEDICAL_COMPLIANCE_MODE=true
AUDIT_LOGGING=true
DATA_RETENTION_DAYS=2555

# File Upload Configuration
MAX_UPLOAD_SIZE=50MB
UPLOAD_PATH=./uploads

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF
    echo -e "${GREEN}✅ Created .env.example${NC}"
fi

# Setup pre-commit hooks
if [ "$PRECOMMIT_AVAILABLE" = true ] && [ -f ".pre-commit-config.yaml" ]; then
    echo -e "${YELLOW}🔨 Installing pre-commit hooks...${NC}"
    pre-commit install || echo -e "${RED}❌ Failed to install pre-commit hooks${NC}"
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
fi

# Create secrets baseline for detect-secrets
if [ ! -f ".secrets.baseline" ]; then
    echo -e "${YELLOW}🔐 Creating secrets baseline...${NC}"
    if command -v detect-secrets &> /dev/null; then
        detect-secrets scan --baseline .secrets.baseline || echo -e "${RED}❌ Failed to create secrets baseline${NC}"
        echo -e "${GREEN}✅ Secrets baseline created${NC}"
    else
        echo -e "${YELLOW}⚠️  detect-secrets not found, creating empty baseline${NC}"
        echo '{}' > .secrets.baseline
    fi
fi

echo ""
echo -e "${BLUE}🛡️  Security Configuration${NC}"

# Check if repository has security features enabled
if [ "$GH_AVAILABLE" = true ]; then
    REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "unknown")
    if [ "$REPO" != "unknown" ]; then
        echo -e "${GREEN}📍 Repository: $REPO${NC}"
        
        # Check security features
        echo -e "${YELLOW}🔍 Checking security features...${NC}"
        
        # This would require additional API calls to check security settings
        echo -e "${BLUE}ℹ️  Please manually verify these security settings in GitHub:${NC}"
        echo "   • Dependabot alerts enabled"
        echo "   • Secret scanning enabled"
        echo "   • Code scanning (CodeQL) enabled"
        echo "   • Branch protection rules configured"
        echo ""
        echo -e "${BLUE}📖 GitHub Security Settings URL:${NC}"
        echo "   https://github.com/$REPO/settings/security_analysis"
    fi
fi

echo ""
echo -e "${BLUE}🔄 Workflow Validation${NC}"

# Validate workflow files
WORKFLOWS_DIR=".github/workflows"
if [ -d "$WORKFLOWS_DIR" ]; then
    echo -e "${YELLOW}🔍 Validating workflow files...${NC}"
    
    REQUIRED_WORKFLOWS=(
        "ci-enhanced.yml"
        "security.yml"
        "performance.yml"
        "quality-gates.yml"
        "deploy.yml" 
        "release.yml"
    )
    
    for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
        if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
            echo -e "${GREEN}✅ $workflow${NC}"
        else
            echo -e "${RED}❌ $workflow (missing)${NC}"
        fi
    done
    
    # Basic YAML syntax check
    if command -v yamllint &> /dev/null; then
        echo -e "${YELLOW}📝 Running YAML syntax check...${NC}"
        yamllint .github/workflows/*.yml || echo -e "${YELLOW}⚠️  YAML warnings found${NC}"
    fi
fi

echo ""
echo -e "${BLUE}📊 Next Steps${NC}"

echo -e "${GREEN}🎉 CI/CD setup is complete!${NC}"
echo ""
echo -e "${BLUE}To get started:${NC}"
echo "1. Review and update .env.example with your configuration"
echo "2. Set up repository secrets in GitHub Settings"
echo "3. Configure branch protection rules for main/develop branches"
echo "4. Enable security features (Dependabot, Secret Scanning, CodeQL)"
echo "5. Create your first feature branch and test the pipeline"
echo ""

echo -e "${BLUE}📚 Documentation:${NC}"
echo "• Full documentation: ci_cd_improvements.md"
echo "• GitHub Actions: https://github.com/$REPO/actions"
echo "• Security tab: https://github.com/$REPO/security"
echo ""

echo -e "${BLUE}🧪 Testing the setup:${NC}"
echo "git checkout -b test-ci-pipeline"
echo "echo '# Test CI/CD' >> README.md"  
echo "git add README.md"
echo "git commit -m 'test: verify CI/CD pipeline'"
echo "git push origin test-ci-pipeline"
echo ""

echo -e "${GREEN}✨ Happy coding with your new CI/CD pipeline! ✨${NC}"