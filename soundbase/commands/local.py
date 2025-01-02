# This script handles the local command.
# Author: Indrajit Ghosh
# Created On: Jan 02, 2025

import click
from rich.panel import Panel
from rich.console import Console

from soundbase.db.database import local_session
from soundbase.db.models import SystemInfo
from soundbase.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.group()
def local():
    """
    Local system-related commands for managing app data.
    
    This group contains commands to interact with the local database to manage 
    system-related information like username, app installation date, and media directory.
    
    Available commands:
    - info: Display the current system information stored in the local database.
    - update: Update the system information such as the username and media directory.
    
    Example usage:
        $ soundbase local info                                      # Displays system information
        $ soundbase local update --username new_username            # Updates the username
        $ soundbase local update --media_dir /new/path/to/media     # Updates media directory
    """
    pass

@local.command()
def info():
    """
    Display the current system information stored in the local database.
    
    This command fetches and displays the current username and media directory 
    from the `SystemInfo` table. If no information is available, it notifies the user.
    
    Example usage:
        $ soundbase local info
    """
    print_basic_info()
    assert_db_init()

    # Fetch system information from the local database
    system_info = local_session.query(SystemInfo).first()
    if system_info:
        system_info.print_on_screen()
    else:
        console.print(Panel("[bold red]System information not found.[/bold red]", border_style="red"))

@local.command()
@click.option('-u', '--username', help="Update the system username")
@click.option('-md', '--media_dir', help="Update the media directory")
def update(username, media_dir):
    """
    Update the system information, such as username or media directory.
    
    This command allows updating the system username or the media directory.
    You can update either one or both at a time. If both fields are provided, 
    both will be updated in the database.
    
    Example usage:
        $ soundbase local update --username new_username
        $ soundbase local update --media_dir "/new/path/to/media"
        $ soundbase local update --username new_username --media_dir "/new/path/to/media"
    """
    print_basic_info()
    assert_db_init()

    # Fetch system information from the local database
    system_info = local_session.query(SystemInfo).first()
    if not system_info:
        console.print(Panel("[bold red]System information not found. Please initialize first.[/bold red]", border_style="red"))
        return

    if username:
        system_info.username = username
        console.print(f"[bold green]Username updated to:[/bold green] {username}")

    if media_dir:
        system_info.media_dir = media_dir
        console.print(f"[bold green]Media directory updated to:[/bold green] {media_dir}")

    try:
        local_session.commit()
        console.print(Panel("[bold green]System information updated successfully.[/bold green]", border_style="green"))
    except Exception as e:
        local_session.rollback()
        console.print(Panel(f"[bold red]Error updating system information: {str(e)}[/bold red]", border_style="red"))
