# Formula 1 MCP Server

A comprehensive Formula 1 MCP server for **puch.ai** that provides access to all Jolpica F1 API endpoints through WhatsApp. Built using the **Jolpica F1 API** (Ergast compatible) for complete F1 data coverage including seasons, circuits, races, constructors, drivers, results, sprint, qualifying, pitstops, laps, standings, and status information.

## Complete Jolpica F1 API Integration

### Core Features (Jolpica F1 API)

- **Next Race Info**: Get upcoming race details with date, time, and location
- **Driver Standings**: Current F1 championship standings with points and wins
- **Constructor Standings**: Team championship standings and points
- **Race Schedule**: Complete season calendar with all race dates
- **Race Results**: Latest race results and finishing positions
- **Historical Data**: Access to all past seasons and race data
- **F1 Trivia**: Random F1 facts, statistics, and interesting information
- **All Seasons**: Browse complete F1 history
- **All Circuits**: Database of F1 tracks and venues
- **Current Drivers**: Full driver lineup for current season
- **Current Constructors**: Complete team lineup
- **Sprint Results**: Sprint race results and analysis
- **Pit Stop Data**: Detailed pit stop analysis and timings
- **Lap Times**: Lap-by-lap timing analysis
- **Qualifying Results**: Complete qualifying session results
- **Driver Profiles**: Comprehensive career statistics
- **Driver Season Performance**: Detailed season breakdowns
- **Race Analysis**: Complete race weekend reports
- **Driver Comparisons**: Head-to-head statistical comparisons
- **Status Codes**: F1 result status classifications

## Quick Start

### 1. Install Dependencies

```bash
# Navigate to project directory
cd f1_mcp_server

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Create .env file with your details:
# AUTH_TOKEN=your_secret_mcp_auth_token
# MY_NUMBER=919876543210
```

### 3. Run the Server

```bash
# Run with new modular structure (recommended)
python main.py

# Or run original single file (still works)
python f1_mcp_server.py
```

### 4. Make Public with ngrok

```bash
# In another terminal
ngrok http 8088
```

### 5. Connect with Puch AI

```
/mcp connect https://your-domain.ngrok.app/mcp your_auth_token
```

## WhatsApp Usage Guide

Once your F1 MCP server is connected to puch.ai, you can use these WhatsApp commands:

### Basic F1 Information

- **"When is the next F1 race?"**
- **"F1 driver standings 2025"**
- **"F1 team standings"**
- **"F1 2025 calendar"**
- **"Latest F1 race results"**
- **"Tell me F1 trivia"**

### Advanced Queries

- **"Show me all F1 circuits"**
- **"F1 seasons history"**
- **"Current F1 drivers"**
- **"Current F1 teams"**
- **"Sprint race results"**
- **"Pit stop analysis"**
- **"Qualifying results"**
- **"F1 status codes"**

### Driver Analysis

- **"Profile of Lewis Hamilton"**
- **"Verstappen 2023 season performance"**
- **"Compare Hamilton vs Verstappen"**

### Historical Data

- **"F1 2018 race schedule"**
- **"2024 round 5 race analysis"**
- **"Monaco 2023 qualifying"**

## API Documentation

### MCP Tools Available (20 F1 Tools + 2 Server Tools = 22 Total)

#### Basic F1 Information Tools

1. **validate** - Confirms MCP server connection
2. **get_next_race** - Next F1 race details
3. **get_current_standings** - Current driver championship standings
4. **get_constructor_standings** - Current team championship standings
5. **get_race_schedule** - Complete race calendar for current season
6. **get_latest_race_results** - Latest race results and positions
7. **f1_trivia** - Random F1 facts and trivia

#### Comprehensive Data Tools

8. **get_all_seasons** - All F1 seasons/years in database
9. **get_all_circuits** - All F1 circuits/tracks ever used
10. **get_current_drivers** - All current season drivers
11. **get_current_constructors** - All current season teams
12. **get_sprint_results** - Sprint race results
13. **get_pitstops** - Pit stop data and analysis
14. **get_lap_times** - Lap timing analysis
15. **get_qualifying_results** - Qualifying session results
16. **get_status_codes** - F1 result status classifications

#### Advanced Analysis Tools

17. **get_historical_schedule** - Historical season calendars
18. **get_driver_profile** - Comprehensive driver career profiles
19. **get_driver_season_performance** - Detailed season breakdowns
20. **get_race_analysis** - Complete race weekend analysis
21. **compare_drivers** - Head-to-head driver comparisons
22. **about** - Get F1 server information

## Jolpica F1 API Endpoints Supported

### All Available Routes

- **seasons** - `/seasons` - All F1 seasons
- **circuits** - `/circuits` - All F1 circuits
- **races** - `/2025/races` - Race calendar
- **constructors** - `/2025/constructors` - Team information
- **drivers** - `/2025/drivers` - Driver information
- **results** - `/2025/results` - Race results
- **sprint** - `/2025/sprint` - Sprint results
- **qualifying** - `/2025/qualifying` - Qualifying results
- **pitstops** - `/2025/1/pitstops` - Pit stop data
- **laps** - `/2025/1/laps` - Lap timing data
- **driverstandings** - `/2025/driverstandings` - Driver championship
- **constructorstandings** - `/2025/constructorstandings` - Team championship
- **status** - `/status` - Result status codes

### API Features

- **Free to use** - No authentication required
- **Ergast compatible** - Familiar API structure
- **Comprehensive** - Current and historical F1 data
- **Reliable** - Community-maintained F1 data source
- **Real-time updates** - Current season data

## Configuration

### Environment Variables

- `AUTH_TOKEN`: MCP authentication token for puch.ai
- `MY_NUMBER`: Your WhatsApp number in format 919876543210
- `MCP_SERVER_HOST`: Server host (default: 0.0.0.0)
- `MCP_SERVER_PORT`: Server port (default: 8088)
- `JOLPICA_BASE_URL`: Jolpica F1 API base URL (default: https://api.jolpi.ca/ergast/f1)

### Project Structure

```
f1_mcp_server/
├── src/                     # Modular source code
│   ├── config.py           # Configuration and constants
│   ├── api_client.py       # Jolpica F1 API client
│   ├── auth.py             # Authentication provider
│   ├── server.py           # Main MCP server setup
│   └── tools/              # F1 tools organized by category
│       ├── basic_tools.py  # validate, about
│       ├── race_tools.py   # race info, schedule, results
│       ├── standings_tools.py # driver & constructor standings
│       ├── driver_tools.py # driver profiles & performance
│       ├── analysis_tools.py # race analysis & comparisons
│       ├── historical_tools.py # historical data
│       ├── data_tools.py   # circuits, drivers, constructors
│       ├── racing_tools.py # sprint, pitstops, lap times
│       ├── status_tools.py # status codes
│       └── trivia_tools.py # F1 trivia
├── tests/                   # Test files
│   └── test_tools.py       # Basic tests
├── main.py                  # Entry point (recommended)
├── f1_mcp_server.py        # Original single file (still works)
├── requirements.txt         # Dependencies
├── .env                     # Environment configuration
└── README.md               # This file
```

## Security & Privacy

- **Bearer token authentication** with puch.ai
- **No data storage** - purely API-driven responses
- **No personal data collection** - only F1 public information
- **Secure API calls** with timeout and error handling

## Troubleshooting

### Common Issues

1. **"No race data found"**:

   - Check if F1 season is active
   - Verify Jolpica F1 API is accessible

2. **"Jolpica F1 API error"**:

   - Check internet connectivity
   - Verify JOLPICA_BASE_URL in .env

3. **Authentication failed**:
   - Verify AUTH_TOKEN in .env
   - Check puch.ai MCP connection

### Debug Commands

```bash
# Test Jolpica F1 API directly
curl "https://api.jolpi.ca/ergast/f1/current.json"

# Check server logs
python main.py  # Watch console output (new structure)
# OR
python f1_mcp_server.py  # Original single file
```

## Ready to Race!

**Status**: COMPLETE - Production-ready F1 MCP Server with comprehensive Jolpica F1 API integration!

Your comprehensive F1 MCP server now provides access to all Jolpica F1 API endpoints, giving you complete F1 data coverage from live championship standings to detailed historical analysis through WhatsApp. With **20 F1 data tools** (22 total including server tools) using the Ergast-compatible API, you have the most comprehensive F1 data access available!

## New Modular Structure Benefits

✅ **Clean Architecture** - Separated concerns with config, API client, auth, and tools
✅ **Easy Maintenance** - Each tool category in dedicated files  
✅ **Better Testing** - Dedicated test structure for reliability
✅ **Flexible Deployment** - Choose `main.py` (new) or `f1_mcp_server.py` (original)
✅ **Scalable Design** - Easy to add new tools and features

**Features**: Real-time race updates + Championship standings + Constructor standings + Historical seasons + Race results + F1 trivia + All circuits + Driver profiles + Season analysis + Qualifying results + Sprint races + Pit stops + Lap times + Driver comparisons + Status codes

---

**Built for F1 fans everywhere! #BuildWithPuch**
