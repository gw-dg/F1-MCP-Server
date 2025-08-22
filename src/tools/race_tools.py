"""
Race information and schedule tools for F1 MCP Server
"""
from datetime import datetime, timezone
from fastmcp import FastMCP
from ..api_client import make_jolpica_request, format_race_datetime
from ..config import logger


def register_race_tools(mcp: FastMCP):
    """Register race tools with the MCP server"""
    
    @mcp.tool(description="Get next F1 race details")
    async def get_next_race() -> str:
        """Get the next upcoming F1 race details"""
        logger.info("Fetching next race details")
        try:
            # Get current date
            current_date = datetime.now(timezone.utc).isoformat()[:10]
            logger.debug(f"Current date: {current_date}")
            
            # Get current race schedule
            logger.debug("Fetching current race schedule")
            data = await make_jolpica_request("current")
            
            if not data or 'MRData' not in data or 'RaceTable' not in data['MRData']:
                logger.warning("No race data found in API response")
                return "🏁 No race data found. API might be unavailable."
            
            races = data['MRData']['RaceTable']['Races']
            if not races:
                logger.warning("Empty race list in API response")
                return "🏁 No upcoming races found. Season might be over."
            
            # Find next race (first one in the current season)
            current_date = datetime.now(timezone.utc).date()
            next_race = None
            
            logger.debug("Searching for next race")
            for race in races:
                race_date = datetime.fromisoformat(race['date']).date()
                logger.debug(f"Checking race: {race['raceName']} on {race_date}")
                if race_date >= current_date:
                    next_race = race
                    logger.info(f"Found next race: {race['raceName']} on {race_date}")
                    break
            
            if not next_race:
                logger.warning("No upcoming races found")
                return "🏁 No upcoming races found for this season."
            
            # Format response
            circuit = next_race['Circuit']
            location = circuit['Location']
            
            response = f"""🏁 **Next F1 Race**

**{next_race['raceName']}**
**Location**: {location['locality']}, {location['country']}
**Circuit**: {circuit['circuitName']}
**Date**: {format_race_datetime(next_race['date'], next_race.get('time'))}
**🏁 Round**: {next_race['round']}

Get ready for some wheel-to-wheel action! 🏎️💨"""

            return response
            
        except Exception as e:
            return f"Failed to get next race: {str(e)}"

    @mcp.tool(description="Get F1 race schedule for current season")
    async def get_race_schedule() -> str:
        """Get F1 race schedule for current season"""
        try:
            current_year = datetime.now().year
            
            # Get current race schedule
            data = await make_jolpica_request("current")
            
            if not data or 'MRData' not in data or 'RaceTable' not in data['MRData']:
                return "No race schedule found. API might be unavailable."
            
            races = data['MRData']['RaceTable']['Races']
            season = data['MRData']['RaceTable']['season']
            
            if not races:
                return f"No races found for {season} season."
            
            response = f"**F1 {season} Race Calendar**\n\n"
            
            current_date = datetime.now(timezone.utc).date()
            
            for race in races:
                race_date = datetime.fromisoformat(race['date']).date()
                status = "✅" if race_date < current_date else "🔜"
                
                circuit = race['Circuit']
                location = circuit['Location']
                
                response += f"{status} **Round {race['round']}: {race['raceName']}**\n"
                response += f"Location: {location['locality']}, {location['country']}\n"
                response += f"Circuit: {circuit['circuitName']}\n"
                response += f"Date: {format_race_datetime(race['date'], race.get('time'))}\n\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get race schedule: {str(e)}"

    @mcp.tool(description="Get latest F1 race results")
    async def get_latest_race_results() -> str:
        """Get latest F1 race results"""
        try:
            # Get latest race results
            data = await make_jolpica_request("current/last/results")
            
            if not data or 'MRData' not in data or 'RaceTable' not in data['MRData']:
                return "🏁 No recent race results available. API might be unavailable."
            
            race_table = data['MRData']['RaceTable']
            if not race_table['Races']:
                return "🏁 No race results found."
            
            race = race_table['Races'][0]
            results = race.get('Results', [])
            
            if not results:
                return "🏁 Race results not available yet."
            
            circuit = race['Circuit']
            location = circuit['Location']
            
            response = f"🏁 **Latest Race Results**\n"
            response += f"**{race['raceName']}** (Round {race['round']})\n"
            response += f"Location: {location['locality']}, {location['country']}\n"
            response += f"Circuit: {circuit['circuitName']}\n"
            response += f"Date: {format_race_datetime(race['date'], race.get('time'))}\n\n"
            
            response += "**Final Positions:**\n"
            for result in results:
                driver = result['Driver']
                constructor = result['Constructor']
                
                response += f"**P{result['position']}: {driver['givenName']} {driver['familyName']}** ({constructor['name']})\n"
                
                # Add time/status
                if 'Time' in result:
                    response += f"   Time: {result['Time']['time']}\n"
                elif 'status' in result:
                    response += f"   Status: {result['status']}\n"
                
                # Add points
                if 'points' in result:
                    response += f"   Points: {result['points']}\n"
                
                response += "\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get race results: {str(e)}"