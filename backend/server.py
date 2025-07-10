#!/usr/bin/env python3

#
# Copyright (c) 2024–2025, Maurice Chat
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import os
from dotenv import load_dotenv

from bot import run_voice_agent

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("WEBSOCKET_HOST", "localhost")
    port = int(os.getenv("WEBSOCKET_PORT", 7860))
    
    print(f"Starting voice agent server on {host}:{port}")
    asyncio.run(run_voice_agent())