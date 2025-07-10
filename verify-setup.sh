#!/bin/bash

# Maurice Chat - Setup Verification Script

echo "🎤 Maurice Chat - Setup Verification"
echo "===================================="
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is installed and running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker Compose is available"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - DEEPGRAM_API_KEY"
    echo
    echo "   Then run this script again."
    exit 1
fi

echo "✅ Environment file exists"

# Validate API keys
source .env

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
    echo "❌ ANTHROPIC_API_KEY is not set in .env file"
    echo "   Get your key from: https://console.anthropic.com/"
    exit 1
fi

if [ -z "$DEEPGRAM_API_KEY" ] || [ "$DEEPGRAM_API_KEY" = "your_deepgram_api_key_here" ]; then
    echo "❌ DEEPGRAM_API_KEY is not set in .env file"
    echo "   Get your key from: https://console.deepgram.com/"
    exit 1
fi

echo "✅ API keys are configured"
echo

echo "🏗️  Building Docker containers..."
echo "   This may take several minutes for the first build..."
if docker-compose build; then
    echo "✅ Docker containers built successfully"
else
    echo "❌ Failed to build Docker containers"
    echo "   Check the error messages above and ensure Docker has enough resources"
    exit 1
fi

echo
echo "🚀 Starting services..."
if docker-compose up -d; then
    echo "✅ Services started successfully"
    echo
    echo "🌟 Maurice Chat is ready!"
    echo
    echo "📱 Frontend: http://localhost:3000"
    echo "🔌 Backend:  http://localhost:7860"
    echo
    echo "💡 To view logs: docker-compose logs -f"
    echo "🛑 To stop:     docker-compose down"
    echo
    echo "🎉 Open http://localhost:3000 and start chatting with Maurice!"
else
    echo "❌ Failed to start services"
    exit 1
fi