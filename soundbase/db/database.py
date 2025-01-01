# db/database.py
# Handles database creation and queries
# Author: Indrajit Ghosh
# Created On: Jan 01, 2024
#
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

# Set the database URL to 'soundbase.db'
DATABASE_URL = "sqlite:///soundbase.db"  # SQLite database file name

# Create an engine and session maker
engine = create_engine(DATABASE_URL, echo=True)  # `echo=True` logs SQL queries to the console
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """
    Initialize the database by creating all tables.
    """
    # Create the tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
