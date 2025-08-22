"""
Status and classification tools for F1 MCP Server
"""
from fastmcp import FastMCP
from ..api_client import make_jolpica_request


def register_status_tools(mcp: FastMCP):
    """Register status tools with the MCP server"""
    
    @mcp.tool(description="Get F1 status codes and DNF reasons")
    async def get_status_codes() -> str:
        """Get all F1 status codes"""
        try:
            data = await make_jolpica_request("status")
            
            if not data or 'MRData' not in data or 'StatusTable' not in data['MRData']:
                return "No status data available."
            
            statuses = data['MRData']['StatusTable'].get('Status', [])
            
            if not statuses:
                return "No status codes found."
            
            response = f"**Formula 1 Status Codes**\n\n"
            response += f"**Total Status Codes:** {len(statuses)}\n\n"
            
            # Group by category
            finished_statuses = []
            retirement_statuses = []
            other_statuses = []
            
            for status in statuses:
                status_text = status.get('status', '').lower()
                if 'finished' in status_text or status_text == '+1 lap' or status_text.startswith('+'):
                    finished_statuses.append(status)
                elif any(word in status_text for word in ['engine', 'gearbox', 'transmission', 'accident', 'collision', 'spun', 'retired', 'withdraw']):
                    retirement_statuses.append(status)
                else:
                    other_statuses.append(status)
            
            if finished_statuses:
                response += f"**RACE COMPLETION:**\n"
                for status in finished_statuses:
                    response += f"  • {status.get('status', 'Unknown')}\n"
                response += "\n"
            
            if retirement_statuses:
                response += f"**RETIREMENTS/DNF:**\n"
                for status in retirement_statuses:
                    response += f"  • {status.get('status', 'Unknown')}\n"
                response += "\n"
            
            if other_statuses:
                response += f"**OTHER STATUS:**\n"
                for status in other_statuses:
                    response += f"  • {status.get('status', 'Unknown')}\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get status codes: {str(e)}"