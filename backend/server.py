#!/usr/bin/env python3

#
# Copyright (c) 2024–2025, Maurice Chat
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from bot import run_bot

# Helper function for text responses
async def get_claude_response_text(user_message: str) -> str:
    """Get Claude response for text messages"""
    try:
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            return "AI service temporarily unavailable. Please try again later."
        
        from anthropic import Anthropic
        client = Anthropic(api_key=anthropic_api_key)
        
        system_prompt = """You are Maurice Rashad's AI assistant. You help potential clients learn about Maurice's background, services, and expertise. Be professional, helpful, and encouraging about contacting Maurice for consultations.

Maurice Rashad is a technology consultant with 10+ years of experience. He offers:

1. Strategic Consulting ($100/month, 2x 1-hour calls)
   - Strategic planning sessions
   - Technology roadmap development
   - Problem-solving workshops
   - Growth strategy recommendations

2. Technology Services ($75/hour)
   - Custom automation solutions
   - Website development & fixes
   - App development
   - Hosting & migration services

3. Expert Workshops ($99 each)
   - AI Agents & Automation
   - Cybersecurity Fundamentals
   - Modern Web Development
   - Cloud Technologies

Contact: mauricerashad@gmail.com
Response time: Within 24 hours
Availability: Global, Remote-First

Key stats: 50+ businesses transformed, 99% client satisfaction, 24/7 support available.

When answering questions:
- Be specific about Maurice's experience and expertise
- Include relevant pricing when discussing services
- Encourage users to contact Maurice for consultations
- Keep responses concise but informative
- Always maintain a professional and friendly tone"""
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        print(f"Claude API error: {e}")
        return "I apologize, but I'm having trouble connecting to the AI service right now. Please try again in a moment, or contact Maurice directly at mauricerashad@gmail.com."

# Helper function for Deepgram speech-to-text
async def process_audio_with_deepgram(base64_audio_data: str) -> str:
    """Process audio data with Deepgram API"""
    try:
        deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        if not deepgram_api_key:
            print("Deepgram API key not configured")
            return ""
        
        import base64
        import httpx
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(base64_audio_data)
        
        # Deepgram API endpoint
        url = "https://api.deepgram.com/v1/listen"
        
        headers = {
            "Authorization": f"Token {deepgram_api_key}",
            "Content-Type": "audio/webm"
        }
        
        params = {
            "model": "nova-2",
            "language": "en-US",
            "smart_format": "true",
            "punctuate": "true",
            "interim_results": "false"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                params=params,
                content=audio_bytes,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                alternatives = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [])
                
                if alternatives and alternatives[0].get("transcript"):
                    transcript = alternatives[0]["transcript"].strip()
                    print(f"Deepgram transcript: {transcript}")
                    return transcript
                else:
                    print("No transcript found in Deepgram response")
                    return ""
            else:
                print(f"Deepgram API error: {response.status_code} - {response.text}")
                return ""
                
    except Exception as e:
        print(f"Deepgram processing error: {e}")
        return ""

# Load environment variables
load_dotenv(override=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles FastAPI startup and shutdown."""
    print("🚀 FastAPI application starting up...")
    print(f"📝 Environment variables loaded:")
    print(f"   - PORT: {os.getenv('PORT', 'Not set')}")
    print(f"   - WEBSOCKET_PORT: {os.getenv('WEBSOCKET_PORT', 'Not set')}")
    print(f"   - WEBSOCKET_HOST: {os.getenv('WEBSOCKET_HOST', 'Not set')}")
    print(f"   - ANTHROPIC_API_KEY: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Not set'}")
    print(f"   - DEEPGRAM_API_KEY: {'Set' if os.getenv('DEEPGRAM_API_KEY') else 'Not set'}")
    yield  # Run app
    print("🛑 FastAPI application shutting down...")


# Initialize FastAPI app with lifespan manager
app = FastAPI(lifespan=lifespan)

# Configure CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f"WebSocket connection attempt from {websocket.client}")
    try:
        await websocket.accept()
        print("WebSocket connection accepted")
        
        # Simple WebSocket handler for now
        await websocket.send_json({
            "type": "connected",
            "message": "Voice chat connected! Start speaking..."
        })
        
        while True:
            try:
                data = await websocket.receive_json()
                print(f"Received WebSocket data: {data}")
                
                if data.get("type") == "audio":
                    # Process audio with Deepgram
                    audio_data = data.get("data", "")
                    if audio_data:
                        transcript = await process_audio_with_deepgram(audio_data)
                        
                        if transcript:
                            # Send live transcription
                            await websocket.send_json({
                                "type": "transcript",
                                "content": transcript
                            })
                            
                            # Get Claude response
                            claude_response = await get_claude_response_text(transcript)
                            
                            # Send final transcript and response
                            await websocket.send_json({
                                "type": "final_transcript",
                                "content": transcript
                            })
                            
                            await websocket.send_json({
                                "type": "response", 
                                "content": claude_response
                            })
                        else:
                            # Send feedback for empty/unclear audio
                            await websocket.send_json({
                                "type": "transcript",
                                "content": "[listening...]"
                            })
                    
                elif data.get("type") == "text":
                    # Handle text messages via WebSocket
                    user_message = data.get("message", "")
                    response = await get_claude_response_text(user_message)
                    await websocket.send_json({
                        "type": "response",
                        "content": response
                    })
                    
            except Exception as e:
                print(f"WebSocket message error: {e}")
                break
                
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        import traceback
        traceback.print_exc()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "maurice-chat-backend", "timestamp": "2024-07-11"}


@app.post("/connect")
async def bot_connect(request: Request) -> Dict[Any, Any]:
    # Get the host from the request to ensure proper connection
    host = request.headers.get("host", "localhost:7860")
    
    # Return RTVI-compatible response format
    return {
        "room_url": f"ws://{host}/ws",
        "ws_url": f"ws://{host}/ws",  # Alternative property name
        "token": "dummy_token",  # Required by some RTVI implementations
        "config": [],  # RTVI config array
        "endpoints": {
            "connect": "/connect",
            "action": "/action"
        }
    }


@app.post("/api/chat")
async def text_chat(request: Request):
    """Handle text-only chat requests (uses Haiku model for speed and cost efficiency)"""
    try:
        body = await request.json()
        user_message = body.get("message", "")
        
        if not user_message:
            return JSONResponse({"error": "Message is required"}, status_code=400)
        
        # Check for required environment variables
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            return JSONResponse({"error": "Anthropic API key not configured"}, status_code=500)
        
        # Import Anthropic client
        from anthropic import Anthropic
        
        client = Anthropic(api_key=anthropic_api_key)
        
        # System prompt for Maurice's AI assistant
        system_prompt = """You are Maurice Rashad's AI assistant. You help potential clients learn about Maurice's background, services, and expertise. Be professional, helpful, and encouraging about contacting Maurice for consultations.

Maurice Rashad is a technology consultant with 10+ years of experience. He offers:

1. Strategic Consulting ($100/month, 2x 1-hour calls)
   - Strategic planning sessions
   - Technology roadmap development
   - Problem-solving workshops
   - Growth strategy recommendations

2. Technology Services ($75/hour)
   - Custom automation solutions
   - Website development & fixes
   - App development
   - Hosting & migration services

3. Expert Workshops ($99 each)
   - AI Agents & Automation
   - Cybersecurity Fundamentals
   - Modern Web Development
   - Cloud Technologies

Contact: mauricerashad@gmail.com
Response time: Within 24 hours
Availability: Global, Remote-First

Key stats: 50+ businesses transformed, 99% client satisfaction, 24/7 support available.

When answering questions:
- Be specific about Maurice's experience and expertise
- Include relevant pricing when discussing services
- Encourage users to contact Maurice for consultations
- Keep responses concise but informative
- Always maintain a professional and friendly tone"""
        
        # Use Claude 3 Haiku for fast, cost-effective text responses
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        return JSONResponse({
            "response": response.content[0].text,
            "model": "claude-3-haiku-20240307",
            "timestamp": "2024-07-11"
        })
        
    except Exception as e:
        print(f"Text chat error: {e}")
        return JSONResponse({"error": "Internal server error"}, status_code=500)


if __name__ == "__main__":
    host = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
    # Railway provides PORT environment variable, fall back to WEBSOCKET_PORT or 7860
    port = int(os.getenv("PORT", os.getenv("WEBSOCKET_PORT", 7860)))
    
    print(f"Starting voice agent server on {host}:{port}")
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    asyncio.run(server.serve())