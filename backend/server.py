#!/usr/bin/env python3

#
# Copyright (c) 2024–2025, Maurice Chat
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import os
import re
from contextlib import asynccontextmanager
from typing import Any, Dict
from datetime import datetime

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator
import resend

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

# Initialize Resend client
resend_client = None
if os.getenv("RESEND_API_KEY"):
    resend_client = resend.Resend(api_key=os.getenv("RESEND_API_KEY"))

# Contact form data model
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    service: str = "General Inquiry"
    message: str
    
    @validator('name', 'message')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('This field is required')
        return v.strip()[:1000]  # Limit length
    
    @validator('service')
    def validate_service(cls, v):
        return v.strip()[:100] if v else "General Inquiry"

def sanitize_html(text: str) -> str:
    """Remove HTML tags and scripts from text"""
    # Remove script tags
    text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    return text.strip()


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
    print(f"   - RESEND_API_KEY: {'Set' if os.getenv('RESEND_API_KEY') else 'Not set'}")
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


@app.post("/api/contact")
async def send_contact_email(contact_data: ContactForm):
    """Handle contact form submissions with Resend email"""
    try:
        if not resend_client:
            raise HTTPException(
                status_code=503, 
                detail="Email service not configured. Please contact mauricerashad@gmail.com directly."
            )
        
        # Sanitize inputs
        sanitized_name = sanitize_html(contact_data.name)
        sanitized_service = sanitize_html(contact_data.service)
        sanitized_message = sanitize_html(contact_data.message)
        
        print(f"📧 Contact form submission from {sanitized_name} ({contact_data.email})")
        
        # Prepare email content
        email_subject = f"🚀 New Contact Form: {sanitized_service}"
        
        email_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
            <div style="background: linear-gradient(135deg, #0EA5E9, #06B6D4); color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -20px -20px 20px -20px;">
                <h1 style="margin: 0; font-size: 24px;">💬 New Contact Form Submission</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">From moewill.github.io</p>
            </div>
            
            <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #0f172a; margin-top: 0; font-size: 18px;">📋 Contact Details</h2>
                <div style="display: grid; gap: 12px;">
                    <div>
                        <strong style="color: #475569;">👤 Name:</strong> 
                        <span style="color: #0f172a;">{sanitized_name}</span>
                    </div>
                    <div>
                        <strong style="color: #475569;">📧 Email:</strong> 
                        <a href="mailto:{contact_data.email}" style="color: #0EA5E9; text-decoration: none;">{contact_data.email}</a>
                    </div>
                    <div>
                        <strong style="color: #475569;">🎯 Service Interest:</strong> 
                        <span style="color: #0f172a; background: #e0f2fe; padding: 4px 8px; border-radius: 4px; font-weight: 500;">{sanitized_service}</span>
                    </div>
                    <div>
                        <strong style="color: #475569;">📅 Submitted:</strong> 
                        <span style="color: #0f172a;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
                    </div>
                </div>
            </div>
            
            <div style="background: white; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                <h3 style="color: #0f172a; margin-top: 0; font-size: 16px; border-bottom: 2px solid #0EA5E9; padding-bottom: 8px;">💭 Message</h3>
                <div style="color: #374151; line-height: 1.6; white-space: pre-wrap; font-size: 15px;">{sanitized_message}</div>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-left: 4px solid #0EA5E9; border-radius: 0 8px 8px 0;">
                <p style="margin: 0; color: #0f172a; font-size: 14px;">
                    <strong>💡 Quick Actions:</strong><br>
                    • Reply directly to respond to {sanitized_name}<br>
                    • Service requested: {sanitized_service}
                </p>
            </div>
            
            <div style="margin-top: 20px; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid #e2e8f0; padding-top: 15px;">
                <p style="margin: 0;">🤖 Powered by Resend via Maurice Chat Backend</p>
            </div>
        </div>
        """
        
        # Send email to Maurice
        email_result = resend_client.emails.send({
            "from": "Maurice Website <onboarding@resend.dev>",
            "to": ["mauricerashad@gmail.com"],
            "reply_to": contact_data.email,
            "subject": email_subject,
            "html": email_html,
            "tags": [
                {"name": "category", "value": "contact-form"},
                {"name": "service", "value": sanitized_service.lower().replace(" ", "-")},
                {"name": "source", "value": "website"}
            ]
        })
        
        print(f"✅ Email sent to Maurice - ID: {email_result.get('id', 'unknown')}")
        
        # Send confirmation email to user
        confirmation_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #0EA5E9, #06B6D4); color: white; padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
                <h1 style="margin: 0; font-size: 28px;">✨ Thank You, {sanitized_name}!</h1>
                <p style="margin: 15px 0 0 0; font-size: 16px; opacity: 0.95;">Your message has been received successfully</p>
            </div>
            
            <div style="background: #f8fafc; padding: 25px; border-radius: 12px; margin-bottom: 20px;">
                <h2 style="color: #0f172a; margin-top: 0; font-size: 20px;">🚀 What happens next?</h2>
                <div style="color: #374151; line-height: 1.8;">
                    <p style="margin: 0 0 15px 0;">
                        <strong style="color: #0EA5E9;">⚡ Quick Response:</strong> I'll get back to you within 24 hours
                    </p>
                    <p style="margin: 0 0 15px 0;">
                        <strong style="color: #0EA5E9;">🎯 Service Focus:</strong> {sanitized_service}
                    </p>
                    <p style="margin: 0;">
                        <strong style="color: #0EA5E9;">💬 Direct Contact:</strong> Feel free to email me directly at 
                        <a href="mailto:mauricerashad@gmail.com" style="color: #0EA5E9;">mauricerashad@gmail.com</a>
                    </p>
                </div>
            </div>
            
            <div style="text-align: center; color: #64748b; font-size: 14px;">
                <p style="margin: 0;">Best regards,<br><strong style="color: #0EA5E9;">Maurice Rashad</strong></p>
                <p style="margin: 10px 0 0 0;">Tech Solutions & Consulting</p>
            </div>
        </div>
        """
        
        try:
            confirmation_result = resend_client.emails.send({
                "from": "Maurice Rashad <onboarding@resend.dev>",
                "to": [contact_data.email],
                "subject": "Thank you for contacting Maurice Rashad - We'll be in touch soon!",
                "html": confirmation_html,
                "tags": [
                    {"name": "category", "value": "confirmation"},
                    {"name": "source", "value": "website"}
                ]
            })
            print(f"✅ Confirmation email sent to {contact_data.email} - ID: {confirmation_result.get('id', 'unknown')}")
        except Exception as conf_error:
            print(f"⚠️ Failed to send confirmation email: {conf_error}")
            # Don't fail the main request if confirmation fails
        
        return JSONResponse({
            "success": True,
            "message": "Message sent successfully! You should receive a confirmation email shortly.",
            "email_id": email_result.get('id'),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Contact form error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send message. Please try again or contact mauricerashad@gmail.com directly."
        )


if __name__ == "__main__":
    host = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
    # Railway provides PORT environment variable, fall back to WEBSOCKET_PORT or 7860
    port = int(os.getenv("PORT", os.getenv("WEBSOCKET_PORT", 7860)))
    
    print(f"Starting voice agent server on {host}:{port}")
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    asyncio.run(server.serve())