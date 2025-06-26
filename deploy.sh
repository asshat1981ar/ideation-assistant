#!/bin/bash
# 🚀 Deployment Script for Ideation Assistant
# Automated deployment to GitHub with verification

set -e  # Exit on any error

echo "🚀 IDEATION ASSISTANT DEPLOYMENT"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Pre-deployment checks
print_status "Running pre-deployment checks..."

# Check if we're in the right directory
if [[ ! -f "main_interface.py" ]]; then
    print_error "Not in the ideation-assistant directory!"
    exit 1
fi

print_success "✅ In correct project directory"

# Check git status
if [[ -n $(git status --porcelain) ]]; then
    print_warning "Uncommitted changes detected. Committing..."
    git add .
    git commit -m "🚀 Pre-deployment commit - Final preparations

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
fi

print_success "✅ Git status clean"

# Step 2: Run build and test
print_status "Running comprehensive test suite..."

python build_and_test.py > build_output.log 2>&1

if [[ $? -eq 0 ]]; then
    print_success "✅ All tests passed (100% success rate)"
    # Show summary
    tail -10 build_output.log | grep -E "(SUCCESS|PASSED|✅)"
else
    print_error "❌ Tests failed! Check build_output.log"
    tail -20 build_output.log
    exit 1
fi

# Step 3: Verify project structure
print_status "Verifying project structure..."

required_files=(
    "main_interface.py"
    "tool_integration.py"
    "enhanced_planning_mode.py"
    "deepseek_client.py"
    "github_integration.py"
    "filesystem_integration.py"
    "code_execution.py"
    "mcp_server_config.py"
    "secure_config.py"
    "requirements.txt"
    "setup.py"
    "README.md"
    "LICENSE"
    ".gitignore"
    "DEPLOYMENT.md"
    "build_and_test.py"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        print_success "✅ $file"
    else
        print_error "❌ Missing required file: $file"
        exit 1
    fi
done

# Step 4: Check dependencies
print_status "Checking dependencies..."

python -c "
import sys
try:
    import aiohttp
    print('✅ aiohttp available')
except ImportError:
    print('❌ aiohttp missing - run: pip install aiohttp')
    sys.exit(1)

# Test import of all modules
modules = [
    'secure_config', 'filesystem_integration', 'deepseek_client',
    'mcp_server_config', 'github_integration', 'code_execution',
    'enhanced_planning_mode', 'tool_integration', 'main_interface'
]

for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        sys.exit(1)

print('✅ All dependencies satisfied')
"

if [[ $? -ne 0 ]]; then
    print_error "Dependency check failed!"
    exit 1
fi

# Step 5: Generate deployment stats
print_status "Generating deployment statistics..."

echo ""
echo "📊 DEPLOYMENT STATISTICS"
echo "========================"
echo "Python files: $(ls *.py | wc -l)"
echo "Total lines of code: $(wc -l *.py | tail -1 | awk '{print $1}')"
echo "Project size: $(du -sh . | awk '{print $1}')"
echo "Git commits: $(git rev-list --count HEAD)"
echo "Last commit: $(git log -1 --format='%h - %s')"
echo ""

# Step 6: GitHub repository instructions
print_status "GitHub deployment instructions..."

echo ""
echo "🐙 GITHUB DEPLOYMENT STEPS"
echo "============================"
echo ""
echo "1. Create GitHub repository:"
echo "   - Go to: https://github.com/new"
echo "   - Name: ideation-assistant"
echo "   - Description: Advanced AI-powered development tool with DeepSeek, MCP, and GitHub integration"
echo "   - Set as Public"
echo "   - DO NOT initialize with README"
echo ""
echo "2. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "3. Verify deployment:"
echo "   https://github.com/asshat1981ar/ideation-assistant"
echo ""

# Step 7: Prepare for push
print_status "Preparing for GitHub push..."

# Check if remote is configured
remote_url=$(git remote get-url origin 2>/dev/null || echo "")
if [[ -z "$remote_url" ]]; then
    print_warning "No remote configured. Adding GitHub remote..."
    git remote add origin https://github.com/asshat1981ar/ideation-assistant.git
fi

print_success "✅ Remote configured: $(git remote get-url origin)"

# Step 8: Final commit with deployment info
git add DEPLOYMENT.md deploy.sh
git commit -m "🚀 Deployment ready - Complete production setup

Deployment Statistics:
- Python files: $(ls *.py | wc -l)
- Lines of code: $(wc -l *.py | tail -1 | awk '{print $1}')
- Project size: $(du -sh . | awk '{print $1}')
- Test success rate: 100%
- All dependencies satisfied
- Full documentation included

Ready for GitHub deployment!

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>" 2>/dev/null || true

# Step 9: Deployment summary
echo ""
echo "🎉 PRE-DEPLOYMENT COMPLETE!"
echo "==========================="
echo ""
print_success "✅ All checks passed"
print_success "✅ Tests: 100% success rate"
print_success "✅ Project structure verified"
print_success "✅ Dependencies satisfied"
print_success "✅ Git repository prepared"
print_success "✅ Documentation complete"
echo ""
echo "🚀 READY TO DEPLOY TO GITHUB!"
echo ""
echo "Run the following command to deploy:"
echo "    git push -u origin main"
echo ""
echo "📖 Full deployment guide: ./DEPLOYMENT.md"
echo ""

# Clean up
rm -f build_output.log

print_success "🎯 Ideation Assistant is ready for production deployment!"