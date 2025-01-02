# This script handles the add-source command.
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025
# 

import click
from rich.console import Console
from rich.panel import Panel

from soundbase.db.models import session, Source
from soundbase.utils.cli_utils import assert_db_init, print_basic_info
from soundbase.utils.db_utils import add_source_to_db

console = Console()

@click.command()
@click.option('-n', '--name', required=True, help='Name of the new source (e.g., YouTube)')
@click.option('-u', '--url', required=True, help='Base URL of the new source (e.g., https://youtube.com)')
def add_source(name, url):
    """
    Add a new source to the SoundBase database.

    This command allows the user to create a new source (e.g., a website for music or video 
    downloads) in the database. A source is identified by its name and base URL. If the source 
    already exists, the user will be notified, and no new source will be created.

    Args:
        name (str): The name of the source, e.g., 'YouTube'.
        url (str): The base URL of the source, e.g., 'https://youtube.com'.

    Example:
        $ soundbase add_source --name "YouTube" --url "https://youtube.com"
    """
    print_basic_info()
    assert_db_init()
    
    # Check if the source already exists
    existing_source = session.query(Source).filter(Source.name == name).first()

    if existing_source:
        console.print(Panel(f"[bold yellow]Source '{name}' already exists.[/bold yellow]", border_style="yellow"))
        return

    # Create and add the new source
    try:
        add_source_to_db(session=session, name=name, base_url=url)
        console.print(Panel(f"[bold green]Source '{name}' created successfully.[/bold green]", border_style="green"))
    except Exception as e:
        session.rollback()
        console.print(Panel(f"[bold red]Error creating source: {str(e)}[/bold red]", border_style="red"))
