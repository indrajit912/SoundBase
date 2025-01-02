# db/database.py
# Handles database creation and queries
# Author: Indrajit Ghosh
# Created On: Jan 01, 2024
#
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from soundbase.config import DATABASE_URL, LOCAL_DB_URL

# Create an engine and session for the database
engine = create_engine(DATABASE_URL)
GlobalSession = sessionmaker(bind=engine)
session = GlobalSession()
Base = declarative_base()

# Local Database
local_engine = create_engine(LOCAL_DB_URL)
LocalSession = sessionmaker(bind=local_engine)
local_session = LocalSession()
LocalBase = declarative_base()
