#
# Copyright (c) 2024–2025, Maurice Chat
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import os
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.serializers.protobuf import ProtobufFrameSerializer
from pipecat.services.anthropic.llm import AnthropicLLMService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

SYSTEM_PROMPT = """You are Maurice, a friendly and helpful AI voice assistant.

Your goal is to have natural, engaging conversations with users.

Guidelines:
- Keep responses concise and conversational (1-2 sentences typically)
- Be warm, friendly, and personable
- Ask follow-up questions to keep the conversation flowing
- Your responses will be converted to speech, so avoid special characters, URLs, or formatting
- Respond naturally as if you're having a real conversation

Start by greeting the user warmly and asking how you can help them today."""


async def run_bot(websocket_client):
    # Check for required environment variables
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    
    if not anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY environment variable is required")
        return
    if not deepgram_api_key:
        logger.error("DEEPGRAM_API_KEY environment variable is required")
        return

    # WebSocket transport for client communication
    ws_transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=ProtobufFrameSerializer(),
        )
    )

    # Speech-to-Text service
    stt = DeepgramSTTService(
        api_key=deepgram_api_key,
        model="nova-2",
        language="en",
        smart_format=True,
    )

    # Text-to-Speech service
    tts = DeepgramTTSService(
        api_key=deepgram_api_key,
        voice="aura-asteria-en",
    )

    # Large Language Model service
    llm = AnthropicLLMService(
        api_key=anthropic_api_key,
        model="claude-3-5-sonnet-20241022",
    )

    # Context management
    context = OpenAILLMContext(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
    )
    context_aggregator = llm.create_context_aggregator(context)

    # RTVI processor for client communication
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # Create pipeline
    pipeline = Pipeline(
        [
            ws_transport.input(),      # Audio input from client
            stt,                       # Speech to text
            context_aggregator.user(), # Add user message to context
            rtvi,                      # RTVI processing
            llm,                       # Generate response
            tts,                       # Text to speech
            ws_transport.output(),     # Audio output to client
            context_aggregator.assistant(), # Add assistant response to context
        ]
    )

    # Create task
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    # Event handlers
    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        logger.info("Client ready - starting conversation")
        await rtvi.set_bot_ready()
        # Start the conversation
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @ws_transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected via FastAPI WebSocket")

    @ws_transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    # Start the pipeline
    runner = PipelineRunner()
    await runner.run(task)