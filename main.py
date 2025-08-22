"""
F1 MCP Server Entry Point

This is the main entry point for the Formula 1 MCP Server.
Run this file to start the server.
"""
import asyncio
from src.server import main

if __name__ == "__main__":
    asyncio.run(main())