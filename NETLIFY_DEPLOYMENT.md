# Maurice Chat - Netlify Deployment Guide

## Overview
This setup provides a simplified HTTP-based chatbot API using Netlify Functions instead of the full WebSocket-based voice system.

## Netlify Setup

### 1. Deploy to Netlify
- Choose the `maurice-chat` repository in Netlify
- Build settings:
  - Build command: `npm run build`
  - Publish directory: `public` (leave empty for functions-only)
  - Functions directory: `netlify/functions`

### 2. Environment Variables
In your Netlify dashboard, add these environment variables:
- `ANTHROPIC_API_KEY`: Your Claude API key (starts with `sk-ant-`)

### 3. Deploy
- Connect your GitHub repository
- Netlify will automatically deploy on push

## API Endpoints

### POST /.netlify/functions/chat
Chat with Maurice AI assistant.

**Request:**
```json
{
  "message": "Tell me about Maurice's services"
}
```

**Response:**
```json
{
  "response": "Maurice offers three main services...",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Integration with Website

Update your website's chatbot to use the Netlify Functions endpoint:

```javascript
// In your website chatbot code
const response = await fetch('https://your-site.netlify.app/.netlify/functions/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: userMessage
  })
});

const data = await response.json();
console.log(data.response);
```

## Limitations

This simplified setup provides:
- ✅ Text-based chat responses
- ✅ Claude AI integration
- ✅ Maurice's business information
- ❌ Real-time voice capabilities
- ❌ WebSocket connections

## For Full Voice Features

For the complete voice chatbot experience, deploy the full backend to:
- Railway.app
- Render.com
- DigitalOcean App Platform
- Google Cloud Run

These platforms support WebSocket connections and long-running processes required for real-time voice chat.