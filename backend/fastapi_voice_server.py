#!/usr/bin/env python3

import asyncio
import base64
import json
import os
from typing import Dict, Any
import uuid
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

app = FastAPI(title="Maurice Voice Chat API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class AudioMessage(BaseModel):
    audio_data: str  # base64 encoded audio
    session_id: str
    format: str = "webm"  # or "wav", "mp3"

class TextMessage(BaseModel):
    message: str
    session_id: str

class VoiceResponse(BaseModel):
    text: str
    audio_url: str
    session_id: str
    timestamp: str

# Session management
active_sessions: Dict[str, Dict[str, Any]] = {}

def get_or_create_session(session_id: str) -> Dict[str, Any]:
    """Get existing session or create new one"""
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now(),
            "conversation_history": [],
            "is_processing": False
        }
    return active_sessions[session_id]

async def process_audio_to_text(audio_data: str, audio_format: str) -> str:
    """Convert audio to text using Deepgram"""
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data)
        
        # This would integrate with Deepgram STT
        # For now, return placeholder
        return "Hello, this is a placeholder transcription"
        
    except Exception as e:
        print(f"STT Error: {e}")
        return "Sorry, I couldn't understand that."

async def generate_ai_response(message: str, conversation_history: list) -> str:
    """Generate AI response using Claude"""
    try:
        # This would integrate with Anthropic API
        # For now, return placeholder
        return f"Thank you for saying: {message}. How else can I help you today?"
        
    except Exception as e:
        print(f"AI Error: {e}")
        return "I'm sorry, I'm having trouble responding right now."

async def text_to_speech(text: str) -> str:
    """Convert text to speech and return audio URL"""
    try:
        # This would integrate with Deepgram TTS
        # For now, return placeholder URL
        return "https://example.com/audio/placeholder.mp3"
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

@app.post("/api/voice/send", response_model=VoiceResponse)
async def send_voice_message(message: AudioMessage, background_tasks: BackgroundTasks):
    """Send voice message and get AI response"""
    session = get_or_create_session(message.session_id)
    
    if session["is_processing"]:
        raise HTTPException(status_code=429, detail="Already processing a message")
    
    session["is_processing"] = True
    
    try:
        # Convert audio to text
        transcribed_text = await process_audio_to_text(message.audio_data, message.format)
        
        # Generate AI response
        ai_response = await generate_ai_response(transcribed_text, session["conversation_history"])
        
        # Convert response to speech
        audio_url = await text_to_speech(ai_response)
        
        # Update conversation history
        session["conversation_history"].extend([
            {"role": "user", "content": transcribed_text},
            {"role": "assistant", "content": ai_response}
        ])
        
        return VoiceResponse(
            text=ai_response,
            audio_url=audio_url,
            session_id=message.session_id,
            timestamp=datetime.now().isoformat()
        )
        
    finally:
        session["is_processing"] = False

@app.post("/api/text/send")
async def send_text_message(message: TextMessage):
    """Send text message and get AI response"""
    session = get_or_create_session(message.session_id)
    
    # Generate AI response
    ai_response = await generate_ai_response(message.message, session["conversation_history"])
    
    # Update conversation history
    session["conversation_history"].extend([
        {"role": "user", "content": message.message},
        {"role": "assistant", "content": ai_response}
    ])
    
    return {
        "response": ai_response,
        "session_id": message.session_id,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/voice/stream/{session_id}")
async def stream_voice_response(session_id: str):
    """Stream AI response as Server-Sent Events"""
    async def generate_stream():
        session = get_or_create_session(session_id)
        
        # This would stream the AI response token by token
        # and TTS chunks as they're generated
        response = "This is a streaming response that would be generated token by token"
        
        for word in response.split():
            yield f"data: {json.dumps({'type': 'text', 'content': word})}\n\n"
            await asyncio.sleep(0.1)  # Simulate streaming delay
        
        # Send final TTS audio
        yield f"data: {json.dumps({'type': 'audio', 'url': 'https://example.com/audio.mp3'})}\n\n"
        yield f"data: {json.dumps({'type': 'end'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    session = get_or_create_session(session_id)
    return {
        "session_id": session_id,
        "created_at": session["created_at"].isoformat(),
        "message_count": len(session["conversation_history"]),
        "is_processing": session["is_processing"]
    }

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session"""
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"message": "Session deleted"}
    return {"message": "Session not found"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "maurice-fastapi-voice",
        "active_sessions": len(active_sessions)
    }

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting FastAPI voice server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)