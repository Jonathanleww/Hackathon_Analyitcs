import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration using environment variables
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'event_analytics'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Chart output configuration
CHART_OUTPUT_DIR = 'results/charts'
CHART_DPI = 300

# Event configuration (customize for your event)
EVENT_CONFIG = {
    'event_name': 'Your Event 2025',
    'event_date': '2025-01-25',  # Reference date for timing calculations
    'meals': [
        'Saturday Lunch',
        'Saturday Dinner', 
        'Sunday Brunch'
    ]
}
