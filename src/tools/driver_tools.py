"""
Driver profile and performance tools for F1 MCP Server
"""
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from ..api_client import make_jolpica_request, get_driver_career_standings
from ..config import logger


def register_driver_tools(mcp: FastMCP):
    """Register driver tools with the MCP server"""
    
    @mcp.tool(description="Get F1 driver profile and career stats")
    async def get_driver_profile(
        driver_id: Annotated[str, Field(description="REQUIRED: Driver ID or surname. Use lowercase surnames like 'hamilton', 'verstappen', 'leclerc', 'russell', 'rosberg', 'schumacher', etc.")] = "hamilton",
    ) -> str:
        """Get comprehensive F1 driver profile and career statistics"""
        logger.info(f"Fetching driver profile for: {driver_id}")
        
        try:
            # Get driver basic info
            driver_data = await make_jolpica_request(f"drivers/{driver_id}")
            
            # Validate driver data structure
            if not driver_data or 'MRData' not in driver_data:
                logger.error(f"Invalid API response structure for driver: {driver_id}")
                return f"❌ Invalid API response for driver '{driver_id}'"
            
            driver_table = driver_data['MRData'].get('DriverTable', {})
            drivers = driver_table.get('Drivers', [])
            
            if not drivers:
                logger.warning(f"No driver found with ID: {driver_id}")
                return f"❌ No driver found with ID '{driver_id}'. Try using driver surname like 'hamilton', 'verstappen', 'leclerc'."
            
            driver = drivers[0]
            driver_name = f"{driver.get('givenName', 'Unknown')} {driver.get('familyName', 'Driver')}"
            logger.info(f"Found driver: {driver_name}")
            
            try:
                # Get driver's championship standings (career) - using helper function
                logger.info(f"Fetching championship standings for {driver_name}")
                standings_data = await get_driver_career_standings(driver_id)
                
                # Get driver's race results (wins and career summary)
                logger.info(f"Fetching race results for {driver_name}")
                results_data = await make_jolpica_request(f"drivers/{driver_id}/results")
            except Exception as data_fetch_error:
                logger.warning(f"Failed to fetch some driver data: {str(data_fetch_error)}")
                standings_data = None
                results_data = None
            
            response = f"**{driver_name} - F1 Career Profile**\n\n"
            
            # Basic Info
            response += f"**📊 Personal Information:**\n"
            if 'permanentNumber' in driver:
                response += f"Car Number: #{driver['permanentNumber']}\n"
            if 'code' in driver:
                response += f"Driver Code: {driver['code']}\n"
            response += f"Nationality: {driver['nationality']}\n"
            if 'dateOfBirth' in driver:
                response += f"Date of Birth: {driver['dateOfBirth']}\n"
            response += "\n"
            
            # Championship History with better error handling
            championships = 0
            recent_seasons = []
            
            if standings_data and 'MRData' in standings_data:
                standings_table = standings_data['MRData'].get('StandingsTable', {})
                standings_lists = standings_table.get('StandingsLists', [])
                
                if standings_lists:
                    logger.info(f"Processing {len(standings_lists)} seasons of standings data")
                    response += f"**🏆 Championship History:**\n"
                    
                    # Process all seasons but show only last 5
                    for season_standings in standings_lists:
                        driver_standings = season_standings.get('DriverStandings', [])
                        if driver_standings:
                            standing = driver_standings[0]
                            season = season_standings.get('season', 'Unknown')
                            
                            try:
                                position = standing.get('position', 'N/A')
                                points = int(standing.get('points', 0))
                                wins = int(standing.get('wins', 0))
                                
                                if position == '1':
                                    championships += 1
                                
                                recent_seasons.append((season, position, points, wins))
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Error processing season {season} data: {str(e)}")
                                continue
                    
                    if championships > 0:
                        response += f"🏆 World Championships: {championships}\n"
                    
                    if recent_seasons:
                        response += f"Recent Seasons Performance:\n"
                        # Show last 5 seasons
                        for season, pos, pts, wins in recent_seasons[-5:]:
                            response += f"  {season}: P{pos} ({pts} pts, {wins} wins)\n"
                        response += "\n"
                else:
                    logger.info(f"No championship standings data available for {driver_name}")
                    response += f"**🏆 Championship History:** No data available\n\n"
            else:
                logger.warning(f"Invalid or missing standings data for {driver_name}")
                response += f"**🏆 Championship History:** Data unavailable\n\n"
            
            # Race Results Summary with enhanced error handling
            if results_data and 'MRData' in results_data:
                race_table = results_data['MRData'].get('RaceTable', {})
                races = race_table.get('Races', [])
                
                if races:
                    logger.info(f"Processing {len(races)} race results for {driver_name}")
                    total_races = len(races)
                    wins = 0
                    podiums = 0
                    points_total = 0
                    dnfs = 0
                    
                    # Count statistics with error handling
                    for race in races:
                        for result in race.get('Results', []):
                            position = result.get('position', 'N/A')
                            
                            if position != 'N/A':
                                try:
                                    pos_int = int(position)
                                    if pos_int == 1:
                                        wins += 1
                                    if pos_int <= 3:
                                        podiums += 1
                                except ValueError:
                                    logger.warning(f"Invalid position in race result: {position}")
                            else:
                                dnfs += 1
                            
                            # Sum points
                            try:
                                points = int(result.get('points', 0))
                                points_total += points
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid points value: {result.get('points')}")
                    
                    response += f"**🏁 Career Statistics:**\n"
                    response += f"Total Races: {total_races}\n"
                    response += f"Race Wins: {wins}\n"
                    response += f"Podiums: {podiums}\n"
                    response += f"Total Points: {points_total}\n"
                    response += f"DNFs: {dnfs}\n"
                    
                    if total_races > 0:
                        win_rate = (wins / total_races) * 100
                        podium_rate = (podiums / total_races) * 100
                        points_per_race = points_total / total_races
                        response += f"Win Rate: {win_rate:.1f}%\n"
                        response += f"Podium Rate: {podium_rate:.1f}%\n"
                        response += f"Avg Points/Race: {points_per_race:.1f}\n"
                    response += "\n"
                    
                    # Recent wins with error handling
                    recent_wins = []
                    for race in races[-20:]:  # Check last 20 races for wins
                        for result in race.get('Results', []):
                            if result.get('position') == '1':
                                season = race.get('season', 'Unknown')
                                race_name = race.get('raceName', 'Unknown Race')
                                recent_wins.append((season, race_name))
                    
                    if recent_wins:
                        response += f"**🏆 Recent Race Wins:**\n"
                        for season, race_name in recent_wins[-5:]:  # Last 5 wins
                            response += f"  {season}: {race_name}\n"
                else:
                    logger.info(f"No race results available for {driver_name}")
                    response += f"**🏁 Career Statistics:** No race data available\n\n"
            else:
                logger.warning(f"Invalid or missing race results data for {driver_name}")
                response += f"**🏁 Career Statistics:** Data unavailable\n\n"
            
            if 'url' in driver:
                response += f"\n🔗 More info: {driver['url']}"
            
            return response
            
        except Exception as e:
            return f"Failed to get driver profile: {str(e)}"

    @mcp.tool(description="Get F1 driver season performance")
    async def get_driver_season_performance(
        driver_id: Annotated[str, Field(description="Driver ID or surname (e.g., 'hamilton', 'verstappen', 'leclerc', 'norris')")] = "verstappen",
        year: Annotated[int, Field(description="Season year to analyze (e.g., 2024, 2023, 2022)")] = 2024,
    ) -> str:
        """Get detailed F1 driver performance for a specific season"""
        try:
            # Get driver's results for the season
            results_data = await make_jolpica_request(f"{year}/drivers/{driver_id}/results")
            
            if not results_data or 'MRData' not in results_data:
                return f"❌ No data found for driver '{driver_id}' in {year} season."
            
            race_table = results_data['MRData']['RaceTable']
            races = race_table.get('Races', [])
            
            if not races:
                return f"❌ No race results found for driver '{driver_id}' in {year}."
            
            # Get driver's championship position for that season
            standings_data = await make_jolpica_request(f"{year}/drivers/{driver_id}/driverStandings")
            
            # Get driver basic info
            driver_data = await make_jolpica_request(f"drivers/{driver_id}")
            driver_name = "Unknown Driver"
            if driver_data and 'MRData' in driver_data and driver_data['MRData']['DriverTable']['Drivers']:
                driver = driver_data['MRData']['DriverTable']['Drivers'][0]
                driver_name = f"{driver['givenName']} {driver['familyName']}"
            
            response = f"🏎️ **{driver_name} - {year} Season Performance**\n\n"
            
            # Season Summary
            total_races = len(races)
            wins = 0
            podiums = 0
            points_finishes = 0
            dnfs = 0
            total_points = 0
            best_finish = 99
            
            race_results = []
            
            for race in races:
                if race['Results']:
                    result = race['Results'][0]  # Driver's result in this race
                    position = result.get('position', 'N/A')
                    points = int(result.get('points', 0))
                    status = result.get('status', 'Unknown')
                    
                    if position != 'N/A':
                        pos_int = int(position)
                        if pos_int == 1:
                            wins += 1
                        if pos_int <= 3:
                            podiums += 1
                        if points > 0:
                            points_finishes += 1
                        if pos_int < best_finish:
                            best_finish = pos_int
                    else:
                        dnfs += 1
                    
                    total_points += points
                    race_results.append((race['round'], race['raceName'], position, points, status))
            
            # Championship Standing
            final_position = "N/A"
            if standings_data and 'MRData' in standings_data:
                standings_lists = standings_data['MRData']['StandingsTable']['StandingsLists']
                if standings_lists and standings_lists[-1]['DriverStandings']:
                    final_position = standings_lists[-1]['DriverStandings'][0]['position']
            
            response += f"**🏆 {year} Championship Performance:**\n"
            response += f"Final Championship Position: P{final_position}\n"
            response += f"Total Points: {total_points}\n"
            response += f"Races Participated: {total_races}\n\n"
            
            response += f"**📊 Season Statistics:**\n"
            response += f"🥇 Wins: {wins}\n"
            response += f"🏆 Podiums: {podiums}\n"
            response += f"📈 Points Finishes: {points_finishes}\n"
            response += f"🚩 DNFs/Retirements: {dnfs}\n"
            response += f"⭐ Best Finish: P{best_finish if best_finish != 99 else 'N/A'}\n"
            
            if total_races > 0:
                response += f"Win Rate: {(wins/total_races)*100:.1f}%\n"
                response += f"Podium Rate: {(podiums/total_races)*100:.1f}%\n"
            response += "\n"
            
            # Race by Race Results (show key races)
            response += f"**🏁 Key Race Results:**\n"
            key_races = []
            
            # Show wins first
            for round_num, race_name, pos, pts, status in race_results:
                if pos == '1':
                    key_races.append(f"🏆 R{round_num} {race_name}: P{pos} ({pts} pts)")
            
            # Then podiums
            for round_num, race_name, pos, pts, status in race_results:
                if pos in ['2', '3']:
                    key_races.append(f"🥇 R{round_num} {race_name}: P{pos} ({pts} pts)")
            
            # Show first 5 key results
            for result in key_races[:5]:
                response += f"{result}\n"
            
            if len(key_races) > 5:
                response += f"... and {len(key_races) - 5} more strong finishes\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get driver season performance: {str(e)}"