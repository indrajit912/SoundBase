# This script handles the init command.
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025
# 

import shutil
import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from sqlalchemy.exc import SQLAlchemyError

from soundbase.db.database import Base, engine, session, LocalBase, local_session, local_engine
from soundbase.db.models import Source, SystemInfo
from soundbase.utils.cli_utils import print_basic_info
from soundbase.utils.db_utils import add_source_to_db
from soundbase.config import DATABASE_PATH, DOT_SOUNDBASE_DIR, DEFAULT_MEDIA_DIR, LOCAL_DB_PATH

console = Console()

@click.command()
def init():
    """
    Initialize the SoundBase database.

    This command sets up the SoundBase database. It checks if the database already exists:
    - If it does not exist, it creates the database and associated tables, 
      including adding a predefined source (YouTube).
    - If the database already exists, the user is prompted to decide whether to 
      delete all existing data and start fresh.

    Example:
        $ soundbase init
    """
    print_basic_info()
    init_db()

def init_db():
    """
    Initialize the database if it does not already exist.
    """
    if not (DATABASE_PATH.exists() or LOCAL_DB_PATH.exists()):
        # Create database and tables if they don't exist
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        try:
            console.rule("[bold cyan]SoundBase Initialization[/bold cyan]")
            console.print("\n")
            
            # Create SoundBase db
            create_soundbase_db()

            # Create the local db
            create_local_db()

            console.print(Panel("[bold green]SoundBase initialized successfully.[/bold green]", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]Error initializing SoundBase: {str(e)}[/bold red]", border_style="red"))
            return

    else:
        console.print(Panel("[bold yellow]SoundBase database already exists.[/bold yellow]", border_style="yellow"))
        res = Prompt.ask("[-] Do you want to delete all existing data and start afresh? (y/n)")
        if res.lower() == 'y':
            shutil.rmtree(DOT_SOUNDBASE_DIR)
            console.print(Panel("[bold red]Existing database deleted.[/bold red]", border_style="red"))
            init_db()  # Recreate the database after deletion

def create_soundbase_db():
    """
    Create the soundbase.db and associated tables (Media, Source).
    """
    try:
        Base.metadata.create_all(engine)
        console.print(Panel("[bold green]SoundBase database (for storing Media and Source tables) created successfully![/bold green]", border_style="green"))
        create_youtube_source()
    except Exception as e:
        console.print(Panel(f"[bold red]Error creating SoundBase database: {str(e)}[/bold red]", border_style="red"))
        return

def create_local_db():
    """
    Create the local database and SystemInfo table.
    
    This function prompts the user to input the system username and media directory 
    to store information about the local system in the database.
    """
    # Create the SystemInfo table if it doesn't already exist
    try:
        LocalBase.metadata.create_all(local_engine)
        console.print(Panel("[bold green]Local database and SystemInfo table created successfully![/bold green]", border_style="green"))
    except Exception as e:
        console.print(Panel(f"[bold red]Error creating local database: {str(e)}[/bold red]", border_style="red"))
        return

    # Prompt for the username and media directory
    username = Prompt.ask("Enter the system username", default=os.getlogin())  # Default to current system username
    media_dir = Prompt.ask("Enter the media directory path", default=DEFAULT_MEDIA_DIR.__str__())

    # Validate the media directory (check if it exists)
    if not os.path.isdir(media_dir):
        console.print(Panel(f"[bold red]The directory '{media_dir}' does not exist! Please provide a valid directory.[/bold red]", border_style="red"))
        return

    # Create and add the system info to the database
    try:
        system_info = SystemInfo(username=username, media_dir=media_dir)
        local_session.add(system_info)
        local_session.commit()
        console.print(Panel(f"[bold green]System Info: {system_info} added to local database.[/bold green]", border_style="green"))
    except SQLAlchemyError as e:
        local_session.rollback()
        console.print(Panel(f"[bold red]Error adding system info: {str(e)}[/bold red]", border_style="red"))


def create_youtube_source():
    """
    Creates a source for YouTube in the database.

    This function checks if a source for YouTube already exists in the database. If it does not 
    exist, it creates and adds the YouTube source (with base URL "https://www.youtube.com") to 
    the database. If the source already exists, it prints a message indicating that the source 
    already exists.

    Example:
        If there is no existing source for YouTube, it will be added to the database 
        with the name "YouTube" and URL "https://www.youtube.com".
    """
    # Check if YouTube source already exists
    existing_source = session.query(Source).filter_by(name="YouTube").first()
    
    if not existing_source:
        add_source_to_db(session=session, name="YouTube", base_url="https://www.youtube.com")
        console.print(Panel("[bold green]YouTube Source added successfully.[/bold green]", border_style="green"))
    else:
        console.print(Panel("[bold yellow]YouTube Source already exists.[/bold yellow]", border_style="yellow"))
