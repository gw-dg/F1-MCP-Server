"""
Formula 1 MCP Server for Puch.ai
Comprehensive F1 data access through Jolpica F1 API (Ergast compatible)
Supports all API routes: seasons, circuits, races, constructors, drivers, results, sprint, qualifying, pitstops, laps, standings, and status
"""
import asyncio
from fastmcp import FastMCP

from .config import (
    TOKEN, MY_NUMBER, MCP_SERVER_HOST, MCP_SERVER_PORT, 
    JOLPICA_BASE_URL, CURRENT_YEAR, logger
)
from .auth import SimpleBearerAuthProvider
from .tools import register_all_tools


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server"""
    # Create MCP server with authentication
    mcp = FastMCP(
        "Formula 1 MCP Server",
        auth=SimpleBearerAuthProvider(TOKEN),
    )
    
    # Register all F1 tools
    register_all_tools(mcp)
    
    return mcp


async def main():
    """Main server entry point"""
    try:
        logger.info("=== Formula 1 MCP Server Starting ===")
        logger.info(f"Server URL: http://{MCP_SERVER_HOST}:{MCP_SERVER_PORT}")
        logger.info(f"Configured phone number: {MY_NUMBER}")
        logger.info(f"Jolpica F1 API endpoint: {JOLPICA_BASE_URL}")
        
        # Log environment configuration
        logger.info("Environment Configuration:")
        logger.info(f"- Current Year: {CURRENT_YEAR}")
        logger.info(f"- Server Host: {MCP_SERVER_HOST}")
        logger.info(f"- Server Port: {MCP_SERVER_PORT}")
        
        # Log feature availability
        logger.info("Available Features:")
        logger.info("- Real-time race data")
        logger.info("- Historical season analysis")
        logger.info("- Driver/Constructor standings")
        logger.info("- Race results and qualifying data")
        logger.info("- Driver comparisons and statistics")
        
        # Create and start the server
        logger.info("Creating MCP server...")
        mcp = create_mcp_server()
        
        logger.info("Starting MCP server...")
        await mcp.run_async("streamable-http", host=MCP_SERVER_HOST, port=MCP_SERVER_PORT)
        logger.info("MCP server started successfully")
        
    except Exception as e:
        logger.critical(f"Failed to start MCP server: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())