#!/bin/bash

# Maurice Chat - Development Setup Script

echo "🛠️  Maurice Chat - Development Setup"
echo "===================================="
echo

# Setup backend
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete"
echo

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "✅ Frontend setup complete"
echo

cd ..

# Check for .env files
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.example .env
fi

if [ ! -f "backend/.env" ]; then
    echo "⚠️  Creating backend/.env file from template..."
    cp backend/.env.example backend/.env
fi

echo
echo "🎯 Development setup complete!"
echo
echo "📝 Next steps:"
echo "1. Edit .env and backend/.env with your API keys"
echo "2. Start backend: cd backend && source venv/bin/activate && python server.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:3000"
echo
echo "🔑 Required API keys:"
echo "- ANTHROPIC_API_KEY (https://console.anthropic.com/)"
echo "- DEEPGRAM_API_KEY (https://console.deepgram.com/)"