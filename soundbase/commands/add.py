# This script handles the add command.
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025
# 

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from soundbase.db.database import session
from soundbase.db.models import Media, Source, Album
from soundbase.utils.cli_utils import assert_db_init, print_basic_info
from soundbase.utils.db_utils import add_media_to_db, add_source_to_db, add_album_to_db

console = Console()

@click.group()
def add():
    """
    Add Command Group.

    The `add` command group provides subcommands to add new entities to the SoundBase database.

    Subcommands:
    - media: Add new media entries (e.g., songs or videos).
    - source: Add a new source (e.g., platforms like YouTube or Spotify).
    - album: Create a new album and optionally associate media entries with it.

    Examples:
        Add a media entry:
        $ soundbase add media -u "https://example.com/media.mp4"

        Add a new source:
        $ soundbase add source -n "YouTube" -u "https://youtube.com"

        Create a new album and associate media entries:
        $ soundbase add album -n "Favorites 2025" -m id1 -m id2
    """
    pass

@add.command()
@click.option('-u', '--url', required=True, help='URL of the media (music/video)')
def media(url):
    """
    Add a new media entry to the SoundBase database.

    This command allows the user to add a new media entry (such as a music or video file) to the 
    database. The user is prompted to select an existing source from the available sources. After 
    selecting the source, the provided URL of the media is stored in the database, associated with 
    the chosen source.

    Args:
        url (str): The URL of the media to be added (e.g., music or video URL).

    Example:
        $ soundbase add --url "https://example.com/media/video1.mp4"
    """
    print_basic_info()
    assert_db_init()
    add_media(url)

def add_media(url):
    sources = session.query(Source).all()
    if not sources:
        console.print("[bold red]No sources available. Please add a source first.[/bold red]")
        return

    console.print("\n[bold green]Available Sources:[/bold green]")
    for index, source in enumerate(sources, start=1):
        console.print(f" {index}. {source.name} - {source.base_url}")
    console.print(" 0. Quit adding and add a new source")

    while True:
        source_choice = Prompt.ask("[-] Select a source by number or 0 to quit")
        if source_choice.isdigit():
            source_choice = int(source_choice)
            if source_choice == 0:
                console.print("[bold yellow]Quitting add process. You can add a source and try again.[/bold yellow]")
                return
            elif 1 <= source_choice <= len(sources):
                break
            else:
                console.print("[bold red]Invalid choice. Please select a valid source number.[/bold red]")
        else:
            console.print("[bold red]Please enter a valid number.[/bold red]")

    selected_source = sources[source_choice - 1]
    console.print(f"[bold cyan]Selected Source:[/bold cyan] {selected_source.name}")

    # Check if the URL already exists in the database
    existing_media = session.query(Media).filter_by(url=url).first()
    if existing_media:
        console.print(Panel(f"[bold yellow]The URL already exists in the database for source: {selected_source.name}[/bold yellow]", border_style="yellow"))
        return

    # Prompt user for the media title
    title = Prompt.ask("Enter the title for the media", default="Untitled")

    # Check if there are albums in the database
    albums = session.query(Album).all()
    album_ids = []
    if albums:
        console.print("\n[bold green]Available Albums:[/bold green]")
        for index, album in enumerate(albums, start=1):
            console.print(f" {index}. {album.name}")
        console.print(" 0. Skip associating an album")

        while True:
            album_choice = Prompt.ask("[-] Select an album by number or 0 to skip")
            if album_choice.isdigit():
                album_choice = int(album_choice)
                if album_choice == 0:
                    console.print("[bold yellow]No album selected. Skipping album association.[/bold yellow]")
                    break
                elif 1 <= album_choice <= len(albums):
                    selected_album = albums[album_choice - 1]
                    album_ids.append(str(selected_album.id))
                    console.print(f"[bold cyan]Selected Album:[/bold cyan] {selected_album.name}")
                    break
                else:
                    console.print("[bold red]Invalid choice. Please select a valid album number.[/bold red]")
            else:
                console.print("[bold red]Please enter a valid number.[/bold red]")

    # Use the add_media_to_db utility function to add the media entry
    result = add_media_to_db(session, url=url, title=title, source_id=selected_source.id, album_ids=album_ids)

    if result["status"] == "success":
        console.print(Panel(f"[bold green]Media added successfully:[/bold green] {result['media_title']}", border_style="green"))
    else:
        console.print(Panel(f"[bold red]Error adding media: {result['message']}[/bold red]", border_style="red"))


@add.command()
@click.option('-n', '--name', required=True, help='Name of the new source (e.g., YouTube)')
@click.option('-u', '--url', required=True, help='Base URL of the new source (e.g., https://youtube.com)')
def source(name, url):
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
    result = add_source_to_db(session=session, name=name, base_url=url)
    
    if result["status"] == "success":
        console.print(Panel(f"[bold green]Source '{name}' created successfully.[/bold green]", border_style="green"))
    else:
        console.print(Panel(f"[bold red]Error creating source: {result['message']}[/bold red]", border_style="red"))

@add.command()
@click.option('-n', '--name', required=True, help='Name of the new album (e.g., "Best of 2025")')
@click.option(
    '-m', '--media-ids',
    multiple=True,
    default=None,
    help='List of media IDs to associate with the album (e.g., -m id1 -m id2)'
)
def album(name, media_ids):
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
