import os
from pathlib import Path
from datetime import date

from dotenv import load_dotenv

# Define the path to the .env file
DOT_ENVPATH = Path(__file__).parent.parent.resolve() / '.env'

# Load the environment variables from the .env file
load_dotenv(DOT_ENVPATH)

# Example environment variable
DEV_MODE = os.getenv('DEV_MODE', 'off')

DOT_SOUNDBASE_DIR = Path.home() / '.soundbase' if DEV_MODE != 'on' else Path.cwd() / '.soundbase'

DEFAULT_MEDIA_DIR = Path.home() / 'Downloads'

DATABASE_PATH = DOT_SOUNDBASE_DIR / 'soundbase.db'
LOCAL_DB_PATH = DOT_SOUNDBASE_DIR / 'local.db'

DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
LOCAL_DB_URL = f'sqlite:///{LOCAL_DB_PATH}'

# Basic information
APP_NAME = "SounBase"
GITHUB_REPO = "https://github.com/indrajit912/SoundBase.git"
CURRENT_YEAR = date.today().year
COPYRIGHT_STATEMENT = f"© {CURRENT_YEAR} Indrajit Ghosh. All rights reserved."
