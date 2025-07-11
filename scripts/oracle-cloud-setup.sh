#!/bin/bash

# Oracle Cloud Quick Setup Script for Maurice Voice Chatbot
# Run this script after SSH'ing into your Oracle Cloud instance

set -e

echo "🚀 Starting Oracle Cloud setup for Maurice Voice Chatbot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Run as ubuntu user."
   exit 1
fi

print_status "Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

print_status "Installing essential tools..."
sudo apt install -y curl wget git htop nano ufw

print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    sudo systemctl start docker
    sudo systemctl enable docker
    print_status "Docker installed successfully"
else
    print_status "Docker already installed"
fi

print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo apt install -y docker-compose
    print_status "Docker Compose installed successfully"
else
    print_status "Docker Compose already installed"
fi

print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 7860
print_status "Firewall configured"

print_status "Cloning Maurice Chat repository..."
if [ ! -d "maurice-chat" ]; then
    git clone https://github.com/moewill/maurice-chat.git
    cd maurice-chat
else
    print_status "Repository already exists, pulling latest changes..."
    cd maurice-chat
    git pull
fi

print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# API Keys - REPLACE WITH YOUR ACTUAL KEYS
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEEPGRAM_API_KEY=your-deepgram-key-here

# Server Configuration
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=7860

# Logging
LOG_LEVEL=INFO
EOF
    print_warning "Created .env file - YOU MUST EDIT IT WITH YOUR API KEYS!"
    print_warning "Run: nano .env"
else
    print_status "Environment file already exists"
fi

print_status "Creating systemd service..."
sudo tee /etc/systemd/system/maurice-chat.service > /dev/null << EOF
[Unit]
Description=Maurice Chat Voice Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/maurice-chat
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable maurice-chat
print_status "Systemd service created and enabled"

print_status "Creating useful aliases..."
echo "
# Maurice Chat aliases
alias chatbot-start='cd ~/maurice-chat && docker-compose up -d'
alias chatbot-stop='cd ~/maurice-chat && docker-compose down'
alias chatbot-logs='cd ~/maurice-chat && docker-compose logs -f'
alias chatbot-status='cd ~/maurice-chat && docker-compose ps'
alias chatbot-restart='cd ~/maurice-chat && docker-compose restart'
" >> ~/.bashrc

print_status "Getting public IP address..."
PUBLIC_IP=$(curl -s ifconfig.me)
print_status "Your public IP: $PUBLIC_IP"

echo ""
echo "🎉 Setup complete! Next steps:"
echo ""
echo "1. Edit your API keys:"
echo "   nano .env"
echo ""
echo "2. Add your actual API keys:"
echo "   - Get Anthropic API key from: https://console.anthropic.com/"
echo "   - Get Deepgram API key from: https://console.deepgram.com/"
echo ""
echo "3. Start the chatbot:"
echo "   chatbot-start"
echo ""
echo "4. Test the deployment:"
echo "   curl http://$PUBLIC_IP:7860/health"
echo ""
echo "5. View logs:"
echo "   chatbot-logs"
echo ""
echo "6. Update your website to use:"
echo "   baseUrl: 'http://$PUBLIC_IP:7860'"
echo ""
print_warning "Remember: You may need to log out and back in for Docker permissions to take effect!"
echo ""
print_status "Happy voice chatting! 🎤"