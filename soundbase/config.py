"""
Configuration Module for SoundBase

This module contains configurations and constants for the SoundBase application. 
It loads environment variables, defines default paths, and sets up database-related 
URLs and other basic application information.

Author: Indrajit Ghosh
Created On: Jan 01, 2025
"""

import os
from pathlib import Path
from datetime import date
from dotenv import load_dotenv

# Define the path to the .env file
DOT_ENVPATH = Path(__file__).parent.parent.resolve() / '.env'
"""
Path to the .env file located at the project's root directory. This file is used 
to load environment-specific variables.
"""

# Load the environment variables from the .env file
load_dotenv(DOT_ENVPATH)

# Example environment variable
DEV_MODE = os.getenv('DEV_MODE', 'off')
"""
Indicates whether the application is running in development mode. Default is 'off'. 
Set to 'on' in the .env file to enable development mode.
"""

# Define the SoundBase configuration directory based on the mode
DOT_SOUNDBASE_DIR = Path.home() / '.soundbase' if DEV_MODE != 'on' else Path.cwd() / '.soundbase'
"""
Default directory for storing SoundBase configurations. If in development mode, 
it uses the current working directory; otherwise, it defaults to the home directory.
"""

# Define the default media directory
DEFAULT_MEDIA_DIR = Path.home() / 'Downloads'
"""
Default directory for storing downloaded media files. Users can customize this path 
to any directory on their system, such as '/media/Music' or '/jellyfin'.
"""

# Define the directory for the main database
DEFAULT_SOUNDBASE_DB_DIR = DOT_SOUNDBASE_DIR
"""
Directory where the main SoundBase database (`soundbase.db`) will be stored.
"""

# Define database file paths
DATABASE_PATH = DEFAULT_SOUNDBASE_DB_DIR / 'soundbase.db'
"""
Path to the main SoundBase database file.
"""

LOCAL_DB_PATH = DOT_SOUNDBASE_DIR / 'local.db'
"""
Path to the local database file used for temporary or local data storage.
"""

# Define database URLs
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
"""
SQLite URL for connecting to the main SoundBase database.
"""

LOCAL_DB_URL = f'sqlite:///{LOCAL_DB_PATH}'
"""
SQLite URL for connecting to the local database.
"""

# Basic application information
APP_NAME = "SoundBase"
"""
Name of the application.
"""

GITHUB_REPO = "https://github.com/indrajit912/SoundBase.git"
"""
URL of the GitHub repository for the SoundBase project.
"""

CURRENT_YEAR = date.today().year
"""
The current year, dynamically fetched using the `datetime.date` module.
"""

COPYRIGHT_STATEMENT = f"© {CURRENT_YEAR} Indrajit Ghosh. All rights reserved."
"""
Copyright statement for the application, dynamically updating with the current year.
"""

