# This script handles the search command.
# Author: Indrajit Ghosh
# Created On: Jan 03, 2025

import click
from rich.panel import Panel
from rich.console import Console

from soundbase.db.database import session
from soundbase.utils.cli_utils import assert_db_init, print_basic_info
from soundbase.utils.db_utils import search_media_in_db

console = Console()

@click.group()
def search():
    """
    Search 

    Available commands:
    - media: Search for media entries based on filters like title, URL, or source_id
    - source: (Another search command for sources, to be implemented)
    
    Example usage:
        $ soundbase search media --title "example title"
        $ soundbase search media --url "http://example.com"
        $ soundbase search media --source_id "123e4567-e89b-12d3-a456-426614174000"                           
    """
    pass

@search.command()
@click.option('-t', '--title', type=str, help="Title of the media to search")
@click.option('-u', '--url', type=str, help="URL of the media to search")
@click.option('-sid', '--source_id', type=str, help="Source ID of the media to search")
def media(title, url, source_id):
    """
    Search for media entries in the database based on the provided filters.
    
    This command allows users to search for media by title, URL, or source ID. 
    If no filters are provided, it returns all available media entries. 
    """
    # Ensure database is initialized and print basic info
    print_basic_info()
    assert_db_init()

    # Ensure only one filter is provided
    filters = sum([bool(title), bool(url), bool(source_id)])
    if filters > 1:
        console.print(Panel("Error: Please provide only one filter at a time (title, url, or source_id).", style="bold red"))
        return

    # Call the utility function to search for media entries
    result = search_media_in_db(session, title=title, url=url, source_id=source_id)

    if result["status"] == "success":
        # If results are found, display them
        console.print(Panel(result["message"], style="bold green"))
        if result["media"]:
            for media in result["media"]:
                console.print(media)
    else:
        # In case of an error, display the message
        console.print(Panel(result["message"], style="bold red"))
