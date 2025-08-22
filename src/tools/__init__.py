"""
F1 MCP Server Tools Registry

This module registers all F1 tools with the MCP server.
Each tool category is defined in separate files for better organization.
"""
from fastmcp import FastMCP

from .basic_tools import register_basic_tools
from .race_tools import register_race_tools
from .standings_tools import register_standings_tools
from .driver_tools import register_driver_tools
from .analysis_tools import register_analysis_tools
from .historical_tools import register_historical_tools
from .data_tools import register_data_tools
from .racing_tools import register_racing_tools
from .status_tools import register_status_tools
from .trivia_tools import register_trivia_tools


def register_all_tools(mcp: FastMCP):
    """Register all F1 tools with the MCP server"""
    
    # Basic validation and info tools
    register_basic_tools(mcp)
    
    # Race information tools
    register_race_tools(mcp)
    
    # Championship standings tools
    register_standings_tools(mcp)
    
    # Driver profile and performance tools
    register_driver_tools(mcp)
    
    # Race analysis and comparison tools
    register_analysis_tools(mcp)
    
    # Historical data tools
    register_historical_tools(mcp)
    
    # Data collection tools (circuits, drivers, constructors)
    register_data_tools(mcp)
    
    # Racing data tools (sprint, pitstops, lap times)
    register_racing_tools(mcp)
    
    # Status and classification tools
    register_status_tools(mcp)
    
    # Trivia and fun fact tools
    register_trivia_tools(mcp)