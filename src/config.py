"""
Configuration and constants for the F1 MCP Server
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('F1_MCP_Server')

# Load environment variables
load_dotenv()

# Environment variables
TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")
MCP_SERVER_HOST = os.environ.get("MCP_SERVER_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.environ.get("MCP_SERVER_PORT", "8087"))
JOLPICA_BASE_URL = os.environ.get("JOLPICA_BASE_URL", "https://api.jolpi.ca/ergast/f1")

# Current F1 season (hardcoded as requested)
CURRENT_YEAR = 2025

# Validation
assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

# F1 Trivia Data
F1_TRIVIA = [
    "Lewis Hamilton holds the record for most pole positions with 104!",
    "Michael Schumacher won 7 World Championships (1994-1995, 2000-2004)",
    "The fastest F1 lap ever was 1:14.260 by Lewis Hamilton at Silverstone 2020",
    "Ferrari is the oldest team in F1, competing since 1950",
    "The most expensive F1 car ever was the McLaren MP4/1 at $50 million",
    "The shortest F1 race was the 2021 Belgian GP - just 3 laps behind safety car",
    "F1 cars can accelerate from 0-200 km/h in less than 5 seconds",
    "Monaco GP is the most prestigious race, held since 1929",
    "F1 engines reach temperatures of over 1000°C during races",
    "Sebastian Vettel won 4 consecutive championships (2010-2013) with Red Bull",
    "The longest F1 race was the 2011 Canadian GP at 4 hours and 4 minutes",
    "Ayrton Senna is considered one of the greatest drivers, with 41 wins and 3 championships",
    "DRS (Drag Reduction System) was introduced in 2011 to increase overtaking",
    "The 2020 Turkish GP saw the first intermediate tire win since 2008",
    "Max Verstappen became the youngest F1 winner at 18 years and 228 days"
]