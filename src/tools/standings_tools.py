"""
Championship standings tools for F1 MCP Server
"""
from typing import Annotated, Optional
from fastmcp import FastMCP
from pydantic import Field
from ..api_client import make_jolpica_request


def register_standings_tools(mcp: FastMCP):
    """Register standings tools with the MCP server"""
    
    @mcp.tool(description="Get F1 driver championship standings")
    async def get_current_standings(
        year: Annotated[Optional[int], Field(description="Season year (e.g., 2023, 2022, 2021) or leave empty for current season")] = None,
    ) -> str:
        """Get F1 driver championship standings for current season or specific year"""
        try:
            # Determine API endpoint based on year parameter
            if year is None:
                endpoint = "current/driverStandings"
            else:
                endpoint = f"{year}/driverStandings"
            
            data = await make_jolpica_request(endpoint)
            
            if not data or 'MRData' not in data or 'StandingsTable' not in data['MRData']:
                return f"No driver standings available for {year if year else 'current season'}. API might be unavailable."
            
            standings_list = data['MRData']['StandingsTable']['StandingsLists']
            if not standings_list:
                return f"No driver standings found for {year if year else 'current season'}."
            
            standings = standings_list[0]['DriverStandings']
            season = data['MRData']['StandingsTable']['season']
            
            # Format response
            response = f"**F1 {season} Driver Championship Standings**\n\n"
            
            for standing in standings:
                driver = standing['Driver']
                constructor = standing['Constructors'][0] if standing['Constructors'] else {'name': 'Unknown'}
                
                response += f"**P{standing['position']}: {driver['givenName']} {driver['familyName']}**\n"
                response += f"Team: {constructor['name']}\n"
                response += f"Points: {standing['points']} | Wins: {standing['wins']}\n"
                response += f"Nationality: {driver['nationality']}\n\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get standings: {str(e)}"

    @mcp.tool(description="Get F1 team championship standings")
    async def get_constructor_standings(
        year: Annotated[Optional[int], Field(description="Season year (e.g., 2023, 2022, 2021) or leave empty for current season")] = None,
    ) -> str:
        """Get F1 constructor championship standings for current season or specific year"""
        try:
            # Determine API endpoint based on year parameter
            if year is None:
                endpoint = "current/constructorStandings"
            else:
                endpoint = f"{year}/constructorStandings"
            
            data = await make_jolpica_request(endpoint)
            
            if not data or 'MRData' not in data or 'StandingsTable' not in data['MRData']:
                return f"No constructor standings available for {year if year else 'current season'}. API might be unavailable."
            
            standings_list = data['MRData']['StandingsTable']['StandingsLists']
            if not standings_list:
                return f"No constructor standings found for {year if year else 'current season'}."
            
            standings = standings_list[0]['ConstructorStandings']
            season = data['MRData']['StandingsTable']['season']
            
            # Format response
            response = f"**F1 {season} Constructor Championship Standings**\n\n"
            
            for standing in standings:
                constructor = standing['Constructor']
                
                response += f"**P{standing['position']}: {constructor['name']}**\n"
                response += f"Nationality: {constructor['nationality']}\n"
                response += f"Points: {standing['points']} | Wins: {standing['wins']}\n\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get constructor standings: {str(e)}"