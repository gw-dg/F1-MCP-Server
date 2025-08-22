"""
API client for Jolpica F1 API and helper functions
"""
import json
from datetime import datetime, timezone
from typing import Optional
import httpx
from mcp import ErrorData, McpError
from mcp.types import INTERNAL_ERROR
from .config import logger, JOLPICA_BASE_URL


async def make_jolpica_request(endpoint: str) -> dict:
    """Make request to Jolpica F1 API with enhanced error handling and logging"""
    logger.info(f"Making API request to endpoint: {endpoint}")
    try:
        url = f"{JOLPICA_BASE_URL}/{endpoint.lstrip('/')}.json"
        logger.info(f"Full URL: {url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info("Sending HTTP GET request...")
            response = await client.get(url)
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            json_data = response.json()
            logger.info(f"Response received - Data structure keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
            
            # Log the structure of MRData if it exists
            if isinstance(json_data, dict) and 'MRData' in json_data:
                mr_data = json_data['MRData']
                logger.info(f"MRData keys: {list(mr_data.keys()) if isinstance(mr_data, dict) else 'MRData not a dict'}")
                
                # Log specific table information
                for table_key in ['DriverTable', 'RaceTable', 'StandingsTable']:
                    if table_key in mr_data:
                        table_data = mr_data[table_key]
                        if isinstance(table_data, dict):
                            logger.info(f"{table_key} keys: {list(table_data.keys())}")
                            # Log count of items
                            for item_key in ['Drivers', 'Races', 'StandingsLists']:
                                if item_key in table_data and isinstance(table_data[item_key], list):
                                    logger.info(f"{table_key}.{item_key} count: {len(table_data[item_key])}")
            else:
                logger.warning("API response does not contain expected 'MRData' key")
                logger.debug(f"Raw response preview: {str(json_data)[:500]}...")
            
            return json_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} for endpoint {endpoint}: {e.response.text}")
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Jolpica F1 API HTTP error {e.response.status_code}: {e.response.text}"
        ))
    except httpx.RequestError as e:
        logger.error(f"Network error for endpoint {endpoint}: {str(e)}")
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Jolpica F1 API network error: {str(e)}"
        ))
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for endpoint {endpoint}: {str(e)}")
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Invalid JSON response from Jolpica F1 API: {str(e)}"
        ))
    except Exception as e:
        logger.error(f"Unexpected error for endpoint {endpoint}: {str(e)}", exc_info=True)
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Jolpica F1 API unexpected error: {str(e)}"
        ))


def format_race_datetime(date_str: str, time_str: Optional[str] = None) -> str:
    """Format race date and time for display"""
    logger.debug(f"Formatting race datetime - date: {date_str}, time: {time_str}")
    try:
        if date_str:
            if time_str:
                # Handle different time formats from API
                if time_str.endswith('Z'):
                    # Format: "05:10:00Z"
                    datetime_str = f"{date_str}T{time_str}"
                elif '+' in time_str or '-' in time_str:
                    # Format: "05:10:00+00:00" 
                    datetime_str = f"{date_str}T{time_str}"
                else:
                    # Format: "05:10:00" (assume UTC)
                    datetime_str = f"{date_str}T{time_str}+00:00"
                
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                formatted = dt.strftime("%B %d, %Y at %H:%M UTC")
                logger.debug(f"Formatted datetime with time: {formatted}")
                return formatted
            else:
                dt = datetime.fromisoformat(date_str)
                formatted = dt.strftime("%B %d, %Y")
                logger.debug(f"Formatted date only: {formatted}")
                return formatted
        logger.warning("Empty date string provided, returning TBD")
        return "TBD"
    except Exception as e:
        logger.error(f"Error formatting race datetime: {str(e)}")
        return f"{date_str} {time_str}" if time_str else date_str


async def get_driver_career_standings(driver_id: str) -> dict:
    """Get driver career standings from recent seasons (API workaround)"""
    logger.info(f"Fetching career standings for driver: {driver_id}")
    
    try:
        current_year = datetime.now().year
        recent_standings = []
        
        # Try to get standings for recent years (last 10 years)
        for year in range(current_year, current_year - 10, -1):
            try:
                year_data = await make_jolpica_request(f"{year}/drivers/{driver_id}/driverStandings")
                if year_data and 'MRData' in year_data:
                    standings_table = year_data['MRData'].get('StandingsTable', {})
                    standings_lists = standings_table.get('StandingsLists', [])
                    if standings_lists:
                        recent_standings.extend(standings_lists)
                        logger.debug(f"Found standings for {driver_id} in {year}")
            except Exception as e:
                logger.debug(f"No standings data for {driver_id} in {year}: {str(e)}")
                continue
        
        # Create mock response structure if we found data
        if recent_standings:
            logger.info(f"Found {len(recent_standings)} seasons of standings data for {driver_id}")
            return {
                'MRData': {
                    'StandingsTable': {
                        'StandingsLists': recent_standings
                    }
                }
            }
        else:
            logger.warning(f"No standings data found for {driver_id}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to fetch career standings for {driver_id}: {str(e)}")
        return None