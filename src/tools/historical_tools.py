"""
Historical data tools for F1 MCP Server
"""
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from ..api_client import make_jolpica_request


def register_historical_tools(mcp: FastMCP):
    """Register historical tools with the MCP server"""
    
    @mcp.tool(description="Get F1 race schedule for specific year")
    async def get_historical_schedule(
        year: Annotated[int, Field(description="Season year (e.g., 2023, 2022, 2021)")] = 2024,
    ) -> str:
        """Get Formula One race calendar for a specific season"""
        try:
            # Get race schedule for specified year
            data = await make_jolpica_request(f"{year}")
            
            if not data or 'MRData' not in data or 'RaceTable' not in data['MRData']:
                return f"No race schedule found for {year}. API might be unavailable."
            
            races = data['MRData']['RaceTable']['Races']
            season = data['MRData']['RaceTable']['season']
            
            if not races:
                return f"No races found for {season} season."
            
            response = f"**F1 {season} Calendar** ({len(races)} races)\n\n"
            
            # Ultra-compact format to avoid MCP session timeout
            for race in races:
                location = race['Circuit']['Location']
                # Just show date without time for brevity
                date_only = race['date']
                
                response += f"R{race['round']}: {race['raceName']} - {location['locality']} ({date_only})\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get {year} schedule: {str(e)}"

    @mcp.tool(description="Get all F1 seasons history")
    async def get_all_seasons() -> str:
        """Get all available F1 seasons"""
        try:
            data = await make_jolpica_request("seasons")
            
            if not data or 'MRData' not in data or 'SeasonTable' not in data['MRData']:
                return "No season data available."
            
            seasons = data['MRData']['SeasonTable'].get('Seasons', [])
            
            if not seasons:
                return "No seasons found."
            
            response = "**Available F1 Seasons**\n\n"
            
            # Group seasons by decades
            decades = {}
            for season in seasons:
                year = int(season['season'])
                decade = (year // 10) * 10
                if decade not in decades:
                    decades[decade] = []
                decades[decade].append(year)
            
            for decade in sorted(decades.keys()):
                years = sorted(decades[decade])
                response += f"**{decade}s:** {', '.join(map(str, years))}\n"
            
            response += f"\n**Total Seasons:** {len(seasons)} (from {seasons[0]['season']} to {seasons[-1]['season']})"
            
            return response
            
        except Exception as e:
            return f"Failed to get seasons: {str(e)}"