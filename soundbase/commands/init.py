# This script handles the init command.
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025
# 

import shutil

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from soundbase.db.models import Base, engine, session, Source
from soundbase.utils.cli_utils import print_basic_info
from soundbase.utils.db_utils import add_source_to_db
from soundbase.config import DATABASE_PATH, DOT_SOUNDBASE_DIR

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

    This function checks if the database exists:
    - If the database does not exist, it creates the necessary tables and adds 
      the YouTube source to the database.
    - If the database already exists, it prompts the user for input to either 
      retain the existing data or delete everything and recreate the database.

    Raises:
        Exception: If there is an error during database creation, it will raise 
        an exception and display an error message.
    """
    if not DATABASE_PATH.exists():
        # Create database and tables if they don't exist
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

        try:
            Base.metadata.create_all(engine)

            console.rule("[bold cyan]SoundBase Initialization[/bold cyan]")
            console.print("\n")
            
            # Create a Source for YouTube
            create_youtube_source()

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
