"""
Basic tests for F1 MCP Server tools
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import create_mcp_server


def test_server_creation():
    """Test that the MCP server can be created without errors"""
    try:
        mcp = create_mcp_server()
        assert mcp is not None
        assert mcp.name == "Formula 1 MCP Server"
        print("Server creation test passed")
    except Exception as e:
        print(f"Server creation test failed: {e}")
        raise


if __name__ == "__main__":
    test_server_creation()
    print("All tests passed!")