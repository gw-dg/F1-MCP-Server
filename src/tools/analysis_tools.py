"""
Race analysis and comparison tools for F1 MCP Server
"""
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from ..api_client import make_jolpica_request, get_driver_career_standings
from ..config import logger


def register_analysis_tools(mcp: FastMCP):
    """Register analysis tools with the MCP server"""
    
    @mcp.tool(description="Get F1 race analysis and results")
    async def get_race_analysis(
        year: Annotated[int, Field(description="Season year (e.g., 2024, 2023, 2022)")] = 2024,
        round_num: Annotated[int, Field(description="Race round number (1-24) or use 'last' for most recent")] = 1,
    ) -> str:
        """Get comprehensive F1 race analysis with qualifying and race results"""
        try:
            # Handle 'last' round
            round_identifier = 'last' if round_num == 0 else str(round_num)
            
            # Get race results
            race_data = await make_jolpica_request(f"{year}/{round_identifier}/results")
            
            # Get qualifying results
            quali_data = await make_jolpica_request(f"{year}/{round_identifier}/qualifying")
            
            if not race_data or 'MRData' not in race_data:
                return f"❌ No race data found for {year} round {round_num}."
            
            race_table = race_data['MRData']['RaceTable']
            races = race_table.get('Races', [])
            
            if not races:
                return f"❌ No race found for {year} round {round_num}."
            
            race = races[0]
            circuit = race['Circuit']
            location = circuit['Location']
            
            response = f"🏁 **{race['raceName']} - {year} Race Analysis**\n\n"
            response += f"**Circuit:** {circuit['circuitName']}\n"
            response += f"**Location:** {location['locality']}, {location['country']}\n"
            response += f"**Date:** {race['date']}\n"
            response += f"🏁 **Round:** {race['round']}\n\n"
            
            # Qualifying Results
            if quali_data and 'MRData' in quali_data and quali_data['MRData']['RaceTable']['Races']:
                quali_race = quali_data['MRData']['RaceTable']['Races'][0]
                if 'QualifyingResults' in quali_race:
                    response += f"**⏱️ QUALIFYING RESULTS:**\n"
                    for i, result in enumerate(quali_race['QualifyingResults'][:10], 1):
                        driver = result['Driver']
                        constructor = result['Constructor']
                        q3_time = result.get('Q3', result.get('Q2', result.get('Q1', 'N/A')))
                        response += f"P{i}: {driver['givenName']} {driver['familyName']} ({constructor['name']}) - {q3_time}\n"
                    response += "\n"
            
            # Race Results
            if 'Results' in race:
                response += f"**🏆 RACE RESULTS:**\n"
                for result in race['Results'][:10]:  # Top 10
                    driver = result['Driver']
                    constructor = result['Constructor']
                    position = result['position']
                    points = result.get('points', '0')
                    
                    # Race time or status
                    time_status = ""
                    if 'Time' in result:
                        time_status = f"({result['Time']['time']})"
                    elif 'status' in result:
                        time_status = f"({result['status']})"
                    
                    response += f"P{position}: {driver['givenName']} {driver['familyName']} ({constructor['name']}) - {points} pts {time_status}\n"
                
                response += "\n"
                
                # Race Winner Details
                if race['Results']:
                    winner = race['Results'][0]
                    winner_driver = winner['Driver']
                    winner_constructor = winner['Constructor']
                    response += f"**🏆 Race Winner:** {winner_driver['givenName']} {winner_driver['familyName']} ({winner_constructor['name']})\n"
                    
                    if 'FastestLap' in winner:
                        fastest = winner['FastestLap']
                        response += f"**⚡ Fastest Lap:** {fastest.get('Time', {}).get('time', 'N/A')} (Lap {fastest.get('lap', 'N/A')})\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get race analysis: {str(e)}"

    @mcp.tool(description="Get F1 qualifying results")
    async def get_qualifying_results(
        year: Annotated[int, Field(description="Season year (e.g., 2024, 2023, 2022)")] = 2024,
        round_num: Annotated[int, Field(description="Race round number (1-24) or 0 for last race")] = 1,
    ) -> str:
        """Get detailed F1 qualifying results with Q1, Q2, Q3 times"""
        try:
            round_identifier = 'last' if round_num == 0 else str(round_num)
            
            quali_data = await make_jolpica_request(f"{year}/{round_identifier}/qualifying")
            
            if not quali_data or 'MRData' not in quali_data:
                return f"❌ No qualifying data found for {year} round {round_num}."
            
            race_table = quali_data['MRData']['RaceTable']
            races = race_table.get('Races', [])
            
            if not races or 'QualifyingResults' not in races[0]:
                return f"❌ No qualifying results found for {year} round {round_num}."
            
            race = races[0]
            circuit = race['Circuit']
            
            response = f"⏱️ **{race['raceName']} - Qualifying Results**\n\n"
            response += f"**Circuit:** {circuit['circuitName']}\n"
            response += f"📅 **Date:** {race['date']}\n\n"
            
            # Qualifying Results
            response += f"**🏁 STARTING GRID:**\n"
            
            q3_drivers = []
            q2_drivers = []
            q1_drivers = []
            
            for result in race['QualifyingResults']:
                driver = result['Driver']
                constructor = result['Constructor']
                position = result['position']
                
                # Determine which session the driver was eliminated in
                if 'Q3' in result:
                    q3_time = result['Q3']
                    q3_drivers.append((position, driver, constructor, q3_time, 'Q3'))
                elif 'Q2' in result:
                    q2_time = result['Q2']
                    q2_drivers.append((position, driver, constructor, q2_time, 'Q2'))
                elif 'Q1' in result:
                    q1_time = result['Q1']
                    q1_drivers.append((position, driver, constructor, q1_time, 'Q1'))
            
            # Show all results in grid order
            all_results = sorted(q3_drivers + q2_drivers + q1_drivers, key=lambda x: int(x[0]))
            
            for pos, driver, constructor, time, session in all_results:
                session_indicator = "🏆" if session == "Q3" else "⚡" if session == "Q2" else "📊"
                response += f"P{pos}: {session_indicator} {driver['givenName']} {driver['familyName']} ({constructor['name']}) - {time}\n"
            
            response += "\n"
            
            # Pole position highlight
            if q3_drivers:
                pole_sitter = min(q3_drivers, key=lambda x: int(x[0]))
                response += f"**🏆 POLE POSITION:** {pole_sitter[1]['givenName']} {pole_sitter[1]['familyName']} ({pole_sitter[2]['name']}) - {pole_sitter[3]}\n"
            
            response += f"\n🏆 Q3 (Top 10) | ⚡ Q2 (P11-15) | 📊 Q1 (P16-20)"
            
            return response
            
        except Exception as e:
            return f"Failed to get qualifying results: {str(e)}"

    @mcp.tool(description="Compare two F1 drivers")
    async def compare_drivers(
        driver1_id: Annotated[str, Field(description="REQUIRED: First driver ID or surname. Use lowercase surnames like 'hamilton', 'verstappen', 'leclerc', 'rosberg', etc.")] = "hamilton",
        driver2_id: Annotated[str, Field(description="REQUIRED: Second driver ID or surname. Use lowercase surnames like 'schumacher', 'vettel', 'alonso', 'rosberg', etc.")] = "verstappen",
        year: Annotated[int, Field(description="Season year to compare (e.g., 2013, 2012, 2021) or 0 for career comparison. Use 0 for career comparison.")] = 0,
    ) -> str:
        """Compare two F1 drivers head-to-head with comprehensive statistics"""
        logger.info(f"Starting driver comparison: {driver1_id} vs {driver2_id}, year: {year if year != 0 else 'career'}")
        
        try:
            # Get both drivers' basic info
            logger.info(f"Fetching driver data for {driver1_id} and {driver2_id}")
            driver1_data = await make_jolpica_request(f"drivers/{driver1_id}")
            driver2_data = await make_jolpica_request(f"drivers/{driver2_id}")
            
            # Validate driver1 data
            if not driver1_data or 'MRData' not in driver1_data:
                logger.error(f"Invalid response structure for driver1: {driver1_id}")
                return f"❌ Invalid API response for driver '{driver1_id}'"
            
            driver_table1 = driver1_data['MRData'].get('DriverTable', {})
            drivers1 = driver_table1.get('Drivers', [])
            
            if not drivers1:
                logger.warning(f"No driver found with ID: {driver1_id}")
                return f"❌ Driver '{driver1_id}' not found. Try using surnames like 'hamilton', 'verstappen', 'leclerc'."
            
            # Validate driver2 data
            if not driver2_data or 'MRData' not in driver2_data:
                logger.error(f"Invalid response structure for driver2: {driver2_id}")
                return f"❌ Invalid API response for driver '{driver2_id}'"
            
            driver_table2 = driver2_data['MRData'].get('DriverTable', {})
            drivers2 = driver_table2.get('Drivers', [])
            
            if not drivers2:
                logger.warning(f"No driver found with ID: {driver2_id}")
                return f"❌ Driver '{driver2_id}' not found. Try using surnames like 'hamilton', 'verstappen', 'leclerc'."
            
            driver1 = drivers1[0]
            driver2 = drivers2[0]
            
            driver1_name = f"{driver1.get('givenName', 'Unknown')} {driver1.get('familyName', 'Driver')}"
            driver2_name = f"{driver2.get('givenName', 'Unknown')} {driver2.get('familyName', 'Driver')}"
            
            logger.info(f"Comparing {driver1_name} vs {driver2_name}")
            
            if year == 0:
                # Career comparison
                response = f"⚔️ **Career Comparison: {driver1_name} vs {driver2_name}**\n\n"
                
                # Get career results for both drivers
                driver1_results = await make_jolpica_request(f"drivers/{driver1_id}/results")
                driver2_results = await make_jolpica_request(f"drivers/{driver2_id}/results")
                
                # Get championship standings for both (career)
                driver1_standings = await get_driver_career_standings(driver1_id)
                driver2_standings = await get_driver_career_standings(driver2_id)
                
            else:
                # Season comparison
                response = f"⚔️ **{year} Season Comparison: {driver1_name} vs {driver2_name}**\n\n"
                
                driver1_results = await make_jolpica_request(f"{year}/drivers/{driver1_id}/results")
                driver2_results = await make_jolpica_request(f"{year}/drivers/{driver2_id}/results")
                
                driver1_standings = await make_jolpica_request(f"{year}/drivers/{driver1_id}/driverStandings")
                driver2_standings = await make_jolpica_request(f"{year}/drivers/{driver2_id}/driverStandings")
            
            # Calculate statistics for both drivers with enhanced error handling
            def calculate_stats(results_data, standings_data, driver_name):
                logger.info(f"Calculating statistics for {driver_name}")
                stats = {
                    'races': 0, 'wins': 0, 'podiums': 0, 'points': 0,
                    'poles': 0, 'fastest_laps': 0, 'championships': 0,
                    'best_championship_pos': 99, 'dnfs': 0
                }
                
                # Process results data
                if results_data and 'MRData' in results_data:
                    race_table = results_data['MRData'].get('RaceTable', {})
                    races = race_table.get('Races', [])
                    stats['races'] = len(races)
                    logger.info(f"{driver_name} participated in {len(races)} races")
                    
                    for race in races:
                        for result in race.get('Results', []):
                            position = result.get('position', 'N/A')
                            
                            # Count valid positions only
                            if position != 'N/A':
                                try:
                                    pos_int = int(position)
                                    if pos_int == 1:
                                        stats['wins'] += 1
                                    if pos_int <= 3:
                                        stats['podiums'] += 1
                                except ValueError:
                                    logger.warning(f"Invalid position value: {position}")
                            else:
                                stats['dnfs'] += 1
                            
                            # Add points
                            try:
                                points = int(result.get('points', 0))
                                stats['points'] += points
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid points value: {result.get('points')}")
                            
                            # Count fastest laps
                            if 'FastestLap' in result:
                                fastest_lap = result['FastestLap']
                                if isinstance(fastest_lap, dict) and fastest_lap.get('rank') == '1':
                                    stats['fastest_laps'] += 1
                else:
                    logger.warning(f"No valid results data for {driver_name}")
                
                # Process standings data
                if standings_data and 'MRData' in standings_data:
                    standings_table = standings_data['MRData'].get('StandingsTable', {})
                    standings_lists = standings_table.get('StandingsLists', [])
                    logger.info(f"{driver_name} has {len(standings_lists)} seasons of standings data")
                    
                    for season_standings in standings_lists:
                        driver_standings = season_standings.get('DriverStandings', [])
                        if driver_standings:
                            standing = driver_standings[0]
                            try:
                                position = int(standing.get('position', 99))
                                if position == 1:
                                    stats['championships'] += 1
                                if position < stats['best_championship_pos']:
                                    stats['best_championship_pos'] = position
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid championship position: {standing.get('position')}")
                else:
                    logger.warning(f"No valid standings data for {driver_name}")
                
                logger.info(f"{driver_name} stats: {stats}")
                return stats
            
            stats1 = calculate_stats(driver1_results, driver1_standings, driver1_name)
            stats2 = calculate_stats(driver2_results, driver2_standings, driver2_name)
            
            # Format comparison
            response += f"**📊 STATISTICAL COMPARISON:**\n"
            response += f"```\n"
            response += f"{'Metric':<20} {'Driver 1':<15} {'Driver 2':<15} {'Winner'}\n"
            response += f"{'-'*20} {'-'*15} {'-'*15} {'-'*10}\n"
            response += f"{'Races':<20} {stats1['races']:<15} {stats2['races']:<15} {'=' if stats1['races']==stats2['races'] else ('1️⃣' if stats1['races']>stats2['races'] else '2️⃣')}\n"
            response += f"{'Wins':<20} {stats1['wins']:<15} {stats2['wins']:<15} {'=' if stats1['wins']==stats2['wins'] else ('1️⃣' if stats1['wins']>stats2['wins'] else '2️⃣')}\n"
            response += f"{'Podiums':<20} {stats1['podiums']:<15} {stats2['podiums']:<15} {'=' if stats1['podiums']==stats2['podiums'] else ('1️⃣' if stats1['podiums']>stats2['podiums'] else '2️⃣')}\n"
            response += f"{'Points':<20} {stats1['points']:<15} {stats2['points']:<15} {'=' if stats1['points']==stats2['points'] else ('1️⃣' if stats1['points']>stats2['points'] else '2️⃣')}\n"
            response += f"{'Championships':<20} {stats1['championships']:<15} {stats2['championships']:<15} {'=' if stats1['championships']==stats2['championships'] else ('1️⃣' if stats1['championships']>stats2['championships'] else '2️⃣')}\n"
            response += f"```\n\n"
            
            # Win rates
            win_rate1 = (stats1['wins'] / stats1['races'] * 100) if stats1['races'] > 0 else 0
            win_rate2 = (stats2['wins'] / stats2['races'] * 100) if stats2['races'] > 0 else 0
            
            podium_rate1 = (stats1['podiums'] / stats1['races'] * 100) if stats1['races'] > 0 else 0
            podium_rate2 = (stats2['podiums'] / stats2['races'] * 100) if stats2['races'] > 0 else 0
            
            response += f"**🎯 SUCCESS RATES:**\n"
            response += f"{driver1_name}: {win_rate1:.1f}% win rate, {podium_rate1:.1f}% podium rate\n"
            response += f"{driver2_name}: {win_rate2:.1f}% win rate, {podium_rate2:.1f}% podium rate\n"
            
            return response
            
        except Exception as e:
            return f"Failed to compare drivers: {str(e)}"