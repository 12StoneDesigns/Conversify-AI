"""Entry point for the Conversify AI application."""

import asyncio
from src.conversify.ai import ConversifyAI

if __name__ == "__main__":
    try:
        ai = ConversifyAI()
        asyncio.run(ai.run())
    except KeyboardInterrupt:
        print("Exiting gracefully...")
