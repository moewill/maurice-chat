#!/bin/bash

# Railway Quick Setup Script
# This script helps you prepare for Railway deployment

set -e

echo "🚀 Railway Setup for Maurice Voice Chatbot"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "backend/server.py" ]; then
    print_error "Please run this script from the maurice-chat directory"
    exit 1
fi

print_success "Repository structure looks good!"

# Check if Docker is installed (for local testing)
if command -v docker &> /dev/null; then
    print_success "Docker is installed (good for local testing)"
else
    print_warning "Docker not found (optional - Railway will build in the cloud)"
fi

# Check if required files exist
if [ -f "Dockerfile" ]; then
    print_success "Dockerfile found"
else
    print_error "Dockerfile not found - this is required for Railway deployment"
    exit 1
fi

if [ -f "requirements.txt" ] || [ -f "backend/requirements.txt" ]; then
    print_success "Requirements file found"
else
    print_error "requirements.txt not found - this is required for Railway deployment"
    exit 1
fi

# Create environment template if it doesn't exist
if [ ! -f "env.example" ]; then
    print_warning "Creating environment template..."
    cat > env.example << 'EOF'
# Maurice Voice Chatbot Environment Variables
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
DEEPGRAM_API_KEY=your-deepgram-key-here
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=7860
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
EOF
    print_success "Created env.example template"
fi

# Check if .env exists (for local development)
if [ -f ".env" ]; then
    print_success ".env file exists for local development"
else
    print_warning ".env file not found - you'll need to set environment variables in Railway"
fi

# Check git status
if git status &> /dev/null; then
    print_success "This is a git repository"
    
    # Check if there are uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes. Consider committing before deploying."
    else
        print_success "Git working directory is clean"
    fi
else
    print_error "This is not a git repository - Railway requires GitHub integration"
    exit 1
fi

# Check if origin is set
if git remote get-url origin &> /dev/null; then
    ORIGIN_URL=$(git remote get-url origin)
    print_success "Git origin is set to: $ORIGIN_URL"
else
    print_error "Git origin not set - you need to push to GitHub first"
    exit 1
fi

echo ""
echo "🎉 Railway Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Go to https://railway.app"
echo "2. Sign up with GitHub"
echo "3. Create new project → Deploy from GitHub repo"
echo "4. Choose your maurice-chat repository"
echo "5. Add environment variables:"
echo "   - ANTHROPIC_API_KEY=sk-ant-your-key-here"
echo "   - DEEPGRAM_API_KEY=your-deepgram-key-here"
echo "   - WEBSOCKET_HOST=0.0.0.0"
echo "   - WEBSOCKET_PORT=7860"
echo "6. Deploy and test!"
echo ""
echo "API Keys needed:"
echo "- Anthropic: https://console.anthropic.com/"
echo "- Deepgram: https://console.deepgram.com/"
echo ""
print_success "Your voice chatbot will be live in ~5 minutes! 🎤"