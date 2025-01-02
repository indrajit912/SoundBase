# This script handles the list command.
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025

import click
from rich.console import Console
from rich.panel import Panel

from soundbase.db.database import session
from soundbase.db.models import Media, Source
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

    Retrieves all media entries from the database and displays them in a structured format,
    utilizing the `print_on_screen()` method from the Media model.
    """
    try:
        media_entries = session.query(Media).order_by(Media.added_on).all()

        if not media_entries:
            console.print(Panel("[bold red]No media entries found in the database.[/bold red]", border_style="red"))
            return

        console.print("[bold cyan]All Media Entries:[/bold cyan]")
        for idx, media in enumerate(media_entries, 1):
            media.print_on_screen(count=idx)
    except Exception as e:
        console.print(Panel(f"[bold red]Error fetching media entries: {e}[/bold red]", border_style="red"))


def list_sources():
    """
    List all sources in the database.

    Retrieves all sources from the database and displays them in a structured format,
    utilizing the `print_on_screen()` method from the Source model.
    """
    try:
        sources = session.query(Source).order_by(Source.name).all()

        if not sources:
            console.print(Panel("[bold red]No sources found in the database.[/bold red]", border_style="red"))
            return

        console.print("[bold cyan]All Sources:[/bold cyan]")
        for idx, source in enumerate(sources, 1):
            source.print_on_screen(count=idx)
    except Exception as e:
        console.print(Panel(f"[bold red]Error fetching sources: {e}[/bold red]", border_style="red"))
