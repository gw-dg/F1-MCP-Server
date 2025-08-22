"""
Data collection tools for F1 MCP Server (circuits, drivers, constructors)
"""
from fastmcp import FastMCP
from ..api_client import make_jolpica_request
from ..config import CURRENT_YEAR


def register_data_tools(mcp: FastMCP):
    """Register data tools with the MCP server"""
    
    @mcp.tool(description="Get all F1 circuits and tracks")
    async def get_all_circuits() -> str:
        """Get all F1 circuits"""
        try:
            data = await make_jolpica_request("circuits")
            
            if not data or 'MRData' not in data or 'CircuitTable' not in data['MRData']:
                return "No circuit data available."
            
            circuits = data['MRData']['CircuitTable'].get('Circuits', [])
            
            if not circuits:
                return "No circuits found."
            
            response = f"**Formula 1 Circuits Database**\n\n"
            response += f"**Total Circuits:** {len(circuits)}\n\n"
            
            # Group by country
            countries = {}
            for circuit in circuits:
                location = circuit.get('Location', {})
                country = location.get('country', 'Unknown')
                if country not in countries:
                    countries[country] = []
                countries[country].append(circuit)
            
            for country in sorted(countries.keys()):
                response += f"**{country}:**\n"
                for circuit in sorted(countries[country], key=lambda x: x.get('circuitName', '')):
                    location = circuit.get('Location', {})
                    locality = location.get('locality', 'Unknown')
                    response += f"  • {circuit.get('circuitName', 'Unknown')} ({locality})\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get circuits: {str(e)}"

    @mcp.tool(description="Get current F1 drivers")
    async def get_current_drivers() -> str:
        """Get all current F1 drivers"""
        try:
            data = await make_jolpica_request("current/drivers")
            
            if not data or 'MRData' not in data or 'DriverTable' not in data['MRData']:
                return "No driver data available."
            
            drivers = data['MRData']['DriverTable'].get('Drivers', [])
            season = data['MRData']['DriverTable'].get('season', CURRENT_YEAR)
            
            if not drivers:
                return f"No drivers found for {season} season."
            
            response = f"**{season} F1 Driver Lineup**\n\n"
            response += f"**Total Drivers:** {len(drivers)}\n\n"
            
            # Group by nationality
            nationalities = {}
            for driver in drivers:
                nationality = driver.get('nationality', 'Unknown')
                if nationality not in nationalities:
                    nationalities[nationality] = []
                nationalities[nationality].append(driver)
            
            for nationality in sorted(nationalities.keys()):
                response += f"**{nationality}:**\n"
                for driver in sorted(nationalities[nationality], key=lambda x: x.get('familyName', '')):
                    name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
                    number = f" (#{driver['permanentNumber']})" if 'permanentNumber' in driver else ""
                    code = f" [{driver['code']}]" if 'code' in driver else ""
                    response += f"  • {name.strip()}{number}{code}\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get current drivers: {str(e)}"

    @mcp.tool(description="Get current F1 teams")
    async def get_current_constructors() -> str:
        """Get all current F1 constructors"""
        try:
            data = await make_jolpica_request("current/constructors")
            
            if not data or 'MRData' not in data or 'ConstructorTable' not in data['MRData']:
                return "No constructor data available."
            
            constructors = data['MRData']['ConstructorTable'].get('Constructors', [])
            season = data['MRData']['ConstructorTable'].get('season', CURRENT_YEAR)
            
            if not constructors:
                return f"No constructors found for {season} season."
            
            response = f"**{season} F1 Constructor Lineup**\n\n"
            response += f"**Total Teams:** {len(constructors)}\n\n"
            
            for constructor in sorted(constructors, key=lambda x: x.get('name', '')):
                name = constructor.get('name', 'Unknown')
                nationality = constructor.get('nationality', 'Unknown')
                response += f"**{name}** ({nationality})\n"
                if 'url' in constructor:
                    response += f"  Link: {constructor['url']}\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            return f"Failed to get current constructors: {str(e)}"