# This script handles the list command.
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025

import click
from rich.console import Console
from rich.panel import Panel
from soundbase.db.models import session, Media, Source
from soundbase.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.option('-m', '--media', is_flag=True, help="List all media entries")
@click.option('-s', '--sources', is_flag=True, help="List all sources")
def list(media, sources):
    """
    List all media entries or all sources in the SoundBase database.

    This command allows the user to list either all media entries or all sources in the 
    database based on the flags provided. The user can choose to list:
    - Media entries (`-m` or `--media`)
    - Sources (`-s` or `--sources`)

    Example:
        $ soundbase list --media
        $ soundbase list --sources
    """
    print_basic_info()
    assert_db_init()

    if media:
        list_media()
    elif sources:
        list_sources()
    else:
        console.print(Panel("[bold red]Please specify either --media or --sources option.[/bold red]", border_style="red"))

def list_media():
    """
    List all media entries in the database.

    This function retrieves all the media entries from the database and displays them in a readable
    format, showing the URL and associated source information.
    """
    media_entries = session.query(Media).all()

    if not media_entries:
        console.print(Panel("[bold red]No media entries found in the database.[/bold red]", border_style="red"))
        return

    console.print("[bold cyan]All Media Entries:[/bold cyan]")
    for idx, media in enumerate(media_entries, 1):
        source = session.query(Source).filter_by(id=media.source_id).first()
        console.print(f"[bold {idx}] URL: {media.url} | Source: {source.name} ({source.base_url})")

def list_sources():
    """
    List all sources in the database.

    This function retrieves all the sources from the database and displays them in a readable format,
    showing the name and base URL of each source.
    """
    sources = session.query(Source).all()

    if not sources:
        console.print(Panel("[bold red]No sources found in the database.[/bold red]", border_style="red"))
        return

    console.print("[bold cyan]All Sources:[/bold cyan]")
    for idx, source in enumerate(sources, 1):
        console.print(f"[bold {idx}] Name: {source.name} | Base URL: {source.base_url}")

