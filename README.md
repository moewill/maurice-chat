# Maurice Chat - AI Voice Agent

A real-time voice chat application powered by Claude AI, featuring speech-to-text, intelligent conversation, and text-to-speech capabilities. Built with Python (Pipecat), TypeScript, and Docker.

## ✨ Features

- **Real-time Voice Conversation**: Speak naturally and get immediate responses
- **Claude AI Integration**: Powered by Anthropic's Claude for intelligent conversations
- **Modern Web Interface**: Beautiful, responsive UI built with Tailwind CSS
- **WebSocket Communication**: Low-latency real-time communication
- **Docker Support**: Easy deployment with Docker containers
- **Speech Recognition**: High-quality STT using Deepgram
- **Natural Voice Synthesis**: Clear TTS using Deepgram

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Frontend      │◄──────────────►│   Backend       │
│   (React/TS)    │                 │   (Python)      │
│   Port: 3000    │                 │   Port: 7860    │
└─────────────────┘                 └─────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │   AI Services   │
                                    │   • Claude AI   │
                                    │   • Deepgram    │
                                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- API Keys:
  - [Anthropic API Key](https://console.anthropic.com/) for Claude AI
  - [Deepgram API Key](https://console.deepgram.com/) for STT/TTS

### 1. Clone and Setup

```bash
git clone https://github.com/moewill/maurice-chat.git
cd maurice-chat
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

### 3. Run with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:7860

## 🛠️ Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run development server
python server.py
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:3000 and will proxy API requests to the backend.

## 📁 Project Structure

```
maurice-chat/
├── backend/                 # Python backend service
│   ├── bot.py              # Main voice agent implementation
│   ├── server.py           # Server entry point
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container
│   └── .env.example        # Environment template
├── frontend/               # TypeScript frontend
│   ├── src/
│   │   ├── main.ts         # Application entry point
│   │   ├── mauriceAgent.ts # Voice agent client
│   │   └── style.css       # Tailwind styles
│   ├── index.html          # Main HTML file
│   ├── package.json        # Node dependencies
│   ├── Dockerfile          # Frontend container
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Multi-service orchestration
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔧 Configuration

### Backend Configuration

Environment variables in `backend/.env`:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=7860
```

### Frontend Configuration

The frontend automatically connects to the backend WebSocket server. For development, update the endpoint in `src/mauriceAgent.ts`:

```typescript
await this.client.connect({
  endpoint: 'http://localhost:7860/connect'
})
```

## 🎯 Usage

1. **Start the Application**: Follow the Quick Start guide above
2. **Open the Web Interface**: Navigate to http://localhost:3000
3. **Grant Microphone Permission**: Click "Allow" when prompted
4. **Start Conversation**: Click "Start Conversation"
5. **Talk to Maurice**: Speak naturally - Maurice will respond with voice
6. **End Conversation**: Click "End Conversation" when done

## 🔊 Voice Features

- **Speech-to-Text**: Real-time transcription of your speech
- **Intelligent Responses**: Claude AI generates contextual replies
- **Text-to-Speech**: Natural voice synthesis for bot responses
- **Voice Activity Detection**: Automatic detection of when you're speaking
- **Low Latency**: Optimized for real-time conversation

## 🐳 Docker Commands

```bash
# Build all services
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose down && docker-compose up --build
```

## 🔍 Troubleshooting

### Common Issues

1. **Microphone Permission Denied**
   - Ensure your browser has microphone access
   - Check browser permissions settings

2. **Connection Failed**
   - Verify backend is running on port 7860
   - Check API keys in `.env` file
   - Ensure ports aren't blocked by firewall

3. **No Audio Output**
   - Check browser audio settings
   - Verify speakers/headphones are working
   - Check browser console for audio errors

4. **API Key Errors**
   - Verify your Anthropic API key is valid
   - Check Deepgram API key is active
   - Ensure sufficient API credits

### Debug Mode

To enable debug logging:

```bash
# Backend logs
docker-compose logs -f backend

# View all logs
docker-compose logs -f
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the BSD 2-Clause License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pipecat AI](https://pipecat.ai/) - Real-time AI conversation framework
- [Anthropic Claude](https://anthropic.com/) - Advanced language model
- [Deepgram](https://deepgram.com/) - Speech recognition and synthesis
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

**Enjoy chatting with Maurice! 🎤✨**