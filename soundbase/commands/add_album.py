# This script handles the add-album command.
# Author: Indrajit Ghosh
# Created On: Jan 03, 2025
#

import click
from rich.console import Console
from rich.panel import Panel

from soundbase.db.database import session
from soundbase.db.models import Album
from soundbase.utils.cli_utils import assert_db_init, print_basic_info
from soundbase.utils.db_utils import add_album_to_db

console = Console()

@click.command()
@click.option('-n', '--name', required=True, help='Name of the new album (e.g., "Best of 2025")')
@click.option(
    '-m', '--media-ids',
    multiple=True,
    default=None,
    help='List of media IDs to associate with the album (e.g., -m id1 -m id2)'
)
def add_album(name, media_ids):
    """
    Add a new album to the SoundBase database.

    This command allows the user to create a new album in the database. Optionally, 
    media entries can be associated with the album using their UUIDs. If the album 
    already exists, the user will be notified, and no new album will be created.

    Args:
        name (str): The name of the album, e.g., "Best of 2025".
        media_ids (list): A list of UUIDs representing media entries to associate 
                          with the album.

    Example:
        $ soundbase add_album --name "Best of 2025" --media-ids id1 id2
    """
    print_basic_info()
    assert_db_init()

    # Check if the album already exists
    existing_album = session.query(Album).filter(Album.name == name).first()

    if existing_album:
        console.print(Panel(f"[bold yellow]Album '{name}' already exists.[/bold yellow]", border_style="yellow"))
        return

    # Create and add the new album
    result = add_album_to_db(session=session, name=name, media_ids=list(media_ids))

    if result["status"] == "success":
        console.print(Panel(f"[bold green]Album '{name}' created successfully.[/bold green]", border_style="green"))
    else:
        console.print(Panel(f"[bold red]Error creating album: {result['message']}[/bold red]", border_style="red"))
