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

from bot import run_bot

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
        await run_bot(websocket)
    except Exception as e:
        print(f"Exception in WebSocket handler: {e}")
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


if __name__ == "__main__":
    host = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
    # Railway provides PORT environment variable, fall back to WEBSOCKET_PORT or 7860
    port = int(os.getenv("PORT", os.getenv("WEBSOCKET_PORT", 7860)))
    
    print(f"Starting voice agent server on {host}:{port}")
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    asyncio.run(server.serve())