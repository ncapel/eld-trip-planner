import os
from dotenv import load_dotenv

load_dotenv()

MAPBOX_ACCESS_TOKEN = os.environ.get('MAPBOX_ACCESS_TOKEN', '')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

# ? hos regulations
HOS_MAX_DRIVING_HOURS = 11.0
HOS_MAX_ON_DUTY_HOURS = 14.0
HOS_REQUIRED_REST_HOURS = 10.0
HOS_MAX_WEEKLY_HOURS = 70.0