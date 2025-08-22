"""
Trivia and fun fact tools for F1 MCP Server
"""
import random
from fastmcp import FastMCP
from ..config import F1_TRIVIA


def register_trivia_tools(mcp: FastMCP):
    """Register trivia tools with the MCP server"""
    
    @mcp.tool(description="Get random F1 trivia and facts")
    async def f1_trivia() -> str:
        """Get random F1 trivia and facts"""
        try:
            trivia = random.choice(F1_TRIVIA)
            
            response = f"""🧠 **F1 Trivia Time!**

{trivia}

💡 Want more F1 facts? Just ask for another trivia!"""
            
            return response
            
        except Exception as e:
            return f"Failed to get F1 trivia: {str(e)}"