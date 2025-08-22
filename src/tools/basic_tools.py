"""
Basic validation and information tools for F1 MCP Server
"""
from fastmcp import FastMCP
from ..config import MY_NUMBER, logger


def register_basic_tools(mcp: FastMCP):
    """Register basic tools with the MCP server"""
    
    @mcp.tool(description="Validate server connection")
    async def validate() -> str:
        """Validate the MCP server connection and return user number"""
        logger.info("Validating MCP server connection")
        if MY_NUMBER is None:
            logger.error("MY_NUMBER environment variable is not set")
            raise ValueError("MY_NUMBER environment variable must be set")
        logger.info(f"Validation successful, returning number: {MY_NUMBER}")
        return MY_NUMBER

    @mcp.tool(description="Get F1 server information")
    async def about() -> dict[str, str]:
        """Get information about the F1 MCP Server"""
        server_name = "Formula 1 MCP Server"
        server_description = """🏎️ Formula 1 in your pocket 🏁

Comprehensive F1 MCP server providing complete access to Formula 1 data through WhatsApp via Puch.ai. 

Built with Jolpica F1 API for real-time race information, championship standings, historical data, driver profiles, race analysis, and F1 trivia.

21 F1 tools covering live races, historical seasons, driver comparisons, qualifying results, pit stops, lap times, and sprint races from 1950 to present.
        """.strip()

        return {
            "name": server_name,
            "description": server_description
        }