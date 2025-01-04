# This script handles the update command.
# Author: Indrajit Ghosh
# Created On: Jan 03, 2025

import click

from rich.panel import Panel
from rich.console import Console

from soundbase.db.database import session
from soundbase.db.models import Source
from soundbase.utils.db_utils import update_media_in_db, update_source_in_db, update_album_in_db
from soundbase.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.group()
def update():
    """
    This script provides commands for updating various entities in the Soundbase database.

    The following entities can be updated:
    1. **Media**: Modify details of a media entry (e.g., title, URL, source ID, associated albums).
    2. **Source**: Update information related to a media source (e.g., name, base URL).
    3. **Album**: Modify album details and associated media entries.

    The available commands allow for selective updates, such as updating a specific field or associating albums or media with other entities.

    Examples:
        # Update the URL of a media entry with the specified ID
        $ soundbase update media --media_id 7c691b98-9d9a-4246-bf3a-b66fa94a4d96 --url <new_url>

        # Update the title of a media entry with the specified ID
        $ soundbase update media --media_id 7c691b98-9d9a-4246-bf3a-b66fa94a4d96 --title <new_title>

        # Update the source of a media entry by selecting a new source interactively
        $ soundbase update media --media_id 7c691b98-9d9a-4246-bf3a-b66fa94a4d96 --source_id

        # Update a source
        $ soundbase update source --id 7c691b98-9d9a-4246-bf3a-b66fa94a4d96 --name <new_name> --base_url "New base URL"

        # Update the name of an album with the specified ID
        $ soundbase update album --album_id 7c691b98-9d9a-4246-bf3a-b66fa94a4d96 --name <new_name>

        # Associate new media entries with an album
        $ soundbase update album --album_id 7c691b98-9d9a-4246-bf3a-b66fa94a4d96 --media-ids id1 id2

        # Update the name of an album and associate new media entries
        $ soundbase update album --album_id 7c691b98-9d9a-4246-bf3a-b66fa94a4d96 --name <new_name> --media-ids id1 id2
    """
    pass


@update.command()
@click.option('-id', '--media_id', required=True, type=str, help="ID of the media to update")
@click.option('-t', '--title', type=str, help="New title of the media")
@click.option('-u', '--url', type=str, help="New URL of the media")
@click.option('-sid', '--source_id', is_flag=True, help="Flag to update the source ID of the media")
@click.option('-aids', '--album_ids', type=str, multiple=True, help="Comma-separated list of album IDs to associate with the media")
@click.option(
    '-a', '--album-ids',
    multiple=True,
    default=None,
    help='List of album IDs to associate with the media (e.g., -a id1 -a id2)'
)
def media(media_id, title, url, source_id, album_ids):
    """
    Update media details in the database.
    
    Parameters:
        - media_id: ID of the media to update (required)
        - title: New title for the media (optional)
        - url: New URL for the media (optional)
        - source_id: Flag to select a new source ID for the media (optional)
        - album_ids: List of album IDs to associate with the media (optional)
    """
    # Ensure database is initialized and print basic info
    print_basic_info()
    assert_db_init()

    # Ensure at least one field is provided to update
    if not any([title, url, source_id, album_ids]):
        console.print(Panel("Error: Please provide at least one field to update (title, URL, source_id, or album_ids).", style="bold red"))
        return

    selected_source_id = None

    if source_id:
        # Fetch all available sources from the database
        sources = session.query(Source).all()

        if not sources:
            console.print(Panel("Error: No sources available in the database.", style="bold red"))
            return

        # Display available sources to the user
        console.print(Panel("Available Sources:", style="bold blue"))
        for index, source in enumerate(sources, start=1):
            console.print(f"{index}. {source.name} (ID: {source.id})")

        # Prompt the user to select a source
        try:
            choice = int(input("\nEnter the number corresponding to the desired source: "))
            if 1 <= choice <= len(sources):
                selected_source_id = sources[choice - 1].id
            else:
                console.print(Panel("Error: Invalid selection. Update aborted.", style="bold red"))
                return
        except ValueError:
            console.print(Panel("Error: Invalid input. Update aborted.", style="bold red"))
            return

    try:
        # Call the update_media_in_db function
        result = update_media_in_db(
            session=session,
            media_id=media_id,
            title=title,
            url=url,
            source_id=selected_source_id,
            album_ids=list(album_ids) if album_ids else None
        )

        # Check the result and provide feedback to the user
        if result["status"] == "success":
            updated_fields = ", ".join([f"{key}: {value}" for key, value in result["updated_fields"].items()])
            console.print(Panel(f"Success: Media with ID {media_id} updated.\nUpdated fields: {updated_fields}", style="bold green"))
        else:
            console.print(Panel(f"Error: {result['message']}", style="bold red"))

    except Exception as e:
        console.print(Panel(f"Unexpected error: {e}", style="bold red"))

@update.command()
@click.option('-id', '--album_id', required=True, type=str, help="ID of the album to update")
@click.option('-n', '--name', type=str, help="New name of the album")
@click.option(
    '-m', '--media-ids',
    multiple=True,
    default=None,
    help='List of media IDs to associate with the album (e.g., -m id1 -m id2)'
)
def album(album_id, name, media_ids):
    """
    Update album details in the database.
    
    Parameters:
        - album_id: ID of the album to update (required)
        - name: New name for the album (optional)
        - media_ids: List of media IDs to associate with the album (optional)
    """
    # Ensure database is initialized and print basic info
    print_basic_info()
    assert_db_init()

    # Ensure at least one field is provided to update
    if not any([name, media_ids]):
        console.print(Panel("Error: Please provide at least one field to update (name or media_ids).", style="bold red"))
        return

    try:
        # Call the update_album_in_db function
        result = update_album_in_db(
            session=session,
            album_id=album_id,
            name=name,
            media_ids=list(media_ids) if media_ids else None
        )

        # Check the result and provide feedback to the user
        if result["status"] == "success":
            updated_fields = ", ".join([f"{key}: {value}" for key, value in result["updated_fields"].items()])
            console.print(Panel(f"Success: Album with ID {album_id} updated.\nUpdated fields: {updated_fields}", style="bold green"))
        else:
            console.print(Panel(f"Error: {result['message']}", style="bold red"))

    except Exception as e:
        console.print(Panel(f"Unexpected error: {e}", style="bold red"))


@update.command()
@click.option('-id', '--source_id', required=True, type=str, help="ID of the source to update")
@click.option('-n', '--name', type=str, help="New name for the source")
@click.option('-u', '--base_url', type=str, help="New base URL for the source")
def source(source_id, name, base_url):
    """
    Update source details in the database.
    
    Parameters:
        - source_id: ID of the source to update (required)
        - name: New name for the source (optional)
        - base_url: New base URL for the source (optional)
    """
    # Ensure database is initialized and print basic info
    print_basic_info()
    assert_db_init()

    # Ensure at least one field is provided to update
    if not any([name, base_url]):
        console.print(Panel("Error: Please provide at least one field to update (name or base_url).", style="bold red"))
        return

    try:
        # Call the update_source_in_db function
        result = update_source_in_db(session=session, source_id=source_id, name=name, base_url=base_url)

        # Check the result and provide feedback to the user
        if result["status"] == "success":
            updated_fields = ", ".join([f"{key}: {value}" for key, value in result["updated_fields"].items()])
            console.print(Panel(f"Success: Source with ID {source_id} updated.\nUpdated fields: {updated_fields}", style="bold green"))
        else:
            console.print(Panel(f"Error: {result['message']}", style="bold red"))

    except Exception as e:
        console.print(Panel(f"Unexpected error: {e}", style="bold red"))
