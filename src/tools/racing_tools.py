"""
Racing data tools for F1 MCP Server (sprint, pitstops, lap times)
"""
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from ..api_client import make_jolpica_request


def register_racing_tools(mcp: FastMCP):
    """Register racing tools with the MCP server"""
    
    @mcp.tool(description="Get F1 sprint race results")
    async def get_sprint_results(
        year: Annotated[int, Field(description="Season year (e.g., 2024, 2023, 2022)")] = 2024,
        round_num: Annotated[int, Field(description="Race round number (1-24) or 0 for last race")] = 1,
    ) -> str:
        """Get F1 sprint race results"""
        try:
            round_identifier = 'last' if round_num == 0 else str(round_num)
            data = await make_jolpica_request(f"{year}/{round_identifier}/sprint")
            
            if not data or 'MRData' not in data or 'RaceTable' not in data['MRData']:
                return f"No sprint data found for {year} round {round_num}."
            
            races = data['MRData']['RaceTable'].get('Races', [])
            
            if not races or 'SprintResults' not in races[0]:
                return f"No sprint results found for {year} round {round_num}."
            
            race = races[0]
            circuit = race['Circuit']
            location = circuit['Location']
            
            response = f"**{race['raceName']} - Sprint Results**\n\n"
            response += f"**Circuit:** {circuit['circuitName']}\n"
            response += f"**Location:** {location['locality']}, {location['country']}\n"
            response += f"**Date:** {race['date']}\n\n"
            
            response += f"**SPRINT RACE RESULTS:**\n"
            for result in race['SprintResults']:
                driver = result['Driver']
                constructor = result['Constructor']
                position = result['position']
                points = result.get('points', '0')
                
                time_status = ""
                if 'Time' in result:
                    time_status = f"({result['Time']['time']})"
                elif 'status' in result:
                    time_status = f"({result['status']})"
                
                response += f"P{position}: {driver['givenName']} {driver['familyName']} ({constructor['name']}) - {points} pts {time_status}\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get sprint results: {str(e)}"

    @mcp.tool(description="Get F1 pit stop data")
    async def get_pitstops(
        year: Annotated[int, Field(description="Season year (e.g., 2024, 2023, 2022)")] = 2024,
        round_num: Annotated[int, Field(description="Race round number (1-24)")] = 1,
    ) -> str:
        """Get F1 pit stop data"""
        try:
            data = await make_jolpica_request(f"{year}/{round_num}/pitstops")
            
            if not data or 'MRData' not in data or 'RaceTable' not in data['MRData']:
                return f"No pit stop data found for {year} round {round_num}."
            
            races = data['MRData']['RaceTable'].get('Races', [])
            
            if not races or 'PitStops' not in races[0]:
                return f"No pit stops found for {year} round {round_num}."
            
            race = races[0]
            circuit = race['Circuit']
            pit_stops = race['PitStops']
            
            response = f"**{race['raceName']} - Pit Stop Analysis**\n\n"
            response += f"**Circuit:** {circuit['circuitName']}\n"
            response += f"**Total Pit Stops:** {len(pit_stops)}\n\n"
            
            # Group by driver
            driver_stops = {}
            fastest_stop = None
            
            for stop in pit_stops:
                driver_id = stop['driverId']
                if driver_id not in driver_stops:
                    driver_stops[driver_id] = []
                driver_stops[driver_id].append(stop)
                
                # Track fastest stop
                if 'duration' in stop:
                    duration = float(stop['duration'])
                    if not fastest_stop or duration < float(fastest_stop.get('duration', 999)):
                        fastest_stop = stop
            
            if fastest_stop:
                response += f"**Fastest Pit Stop:** {fastest_stop['duration']}s (Lap {fastest_stop['lap']})\n\n"
            
            response += f"**PIT STOP SUMMARY BY DRIVER:**\n"
            for driver_id in sorted(driver_stops.keys()):
                stops = driver_stops[driver_id]
                avg_time = sum(float(s.get('duration', 0)) for s in stops) / len(stops)
                response += f"**{driver_id.upper()}:** {len(stops)} stops, avg {avg_time:.2f}s\n"
                for stop in stops:
                    response += f"  • Lap {stop['lap']}: {stop.get('duration', 'N/A')}s\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get pit stop data: {str(e)}"

    @mcp.tool(description="Get F1 lap times")
    async def get_lap_times(
        year: Annotated[int, Field(description="Season year (e.g., 2024, 2023, 2022)")] = 2024,
        round_num: Annotated[int, Field(description="Race round number (1-24)")] = 1,
    ) -> str:
        """Get F1 lap times (limited to avoid overwhelming data)"""
        try:
            data = await make_jolpica_request(f"{year}/{round_num}/laps")
            
            if not data or 'MRData' not in data or 'RaceTable' not in data['MRData']:
                return f"No lap time data found for {year} round {round_num}."
            
            races = data['MRData']['RaceTable'].get('Races', [])
            
            if not races or 'Laps' not in races[0]:
                return f"No lap times found for {year} round {round_num}."
            
            race = races[0]
            circuit = race['Circuit']
            laps = race['Laps']
            
            response = f"**{race['raceName']} - Lap Time Analysis**\n\n"
            response += f"**Circuit:** {circuit['circuitName']}\n"
            response += f"**Total Laps:** {len(laps)}\n\n"
            
            # Find fastest lap overall
            fastest_lap = None
            fastest_time = None
            
            for lap in laps:
                for timing in lap.get('Timings', []):
                    if 'time' in timing:
                        time_str = timing['time']
                        # Convert lap time to seconds for comparison
                        try:
                            parts = time_str.split(':')
                            if len(parts) == 2:
                                minutes = int(parts[0])
                                seconds = float(parts[1])
                                total_seconds = minutes * 60 + seconds
                                
                                if not fastest_time or total_seconds < fastest_time:
                                    fastest_time = total_seconds
                                    fastest_lap = {
                                        'lap': lap['number'],
                                        'driver': timing['driverId'],
                                        'time': time_str
                                    }
                        except (ValueError, IndexError):
                            continue
            
            if fastest_lap:
                response += f"**Fastest Lap:** {fastest_lap['time']} by {fastest_lap['driver'].upper()} (Lap {fastest_lap['lap']})\n\n"
            
            # Show sample lap times (first 5 laps)
            response += f"**SAMPLE LAP TIMES (First 5 Laps):**\n"
            for lap in laps[:5]:
                lap_num = lap['number']
                response += f"**Lap {lap_num}:**\n"
                
                timings = lap.get('Timings', [])
                # Show top 5 drivers for this lap
                for timing in timings[:5]:
                    driver = timing['driverId'].upper()
                    time = timing.get('time', 'N/A')
                    position = timing.get('position', 'N/A')
                    response += f"  P{position} {driver}: {time}\n"
                response += "\n"
            
            if len(laps) > 5:
                response += f"... and {len(laps) - 5} more laps\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get lap times: {str(e)}"