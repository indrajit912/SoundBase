# This script handles the del command.
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025
#

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from soundbase.db.models import session, Media, Source
from soundbase.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.option('-m', '--media', is_flag=True, help="Delete media entries")
@click.option('-s', '--source', is_flag=True, help="Delete sources")
def delete(media, source):
    """
    Delete a source or media entry from the SoundBase database.

    This command allows the user to delete either a source or a media entry from the database.
    The user must specify whether they want to delete a source or media by using the appropriate 
    flags: `--source` for deleting sources or `--media` for deleting media.

    Options:
        -m, --media   Delete media entries from the database.
        -s, --source  Delete sources from the database.

    Example Usage:
        To delete a source:
            $ soundbase delete --source

        To delete a media entry:
            $ soundbase delete --media

    Notes:
        - Deleting a source is not allowed if it is associated with any media entries.
        - If neither `--source` nor `--media` is provided, the command will prompt the user 
          to specify one of the options.
    """
    print_basic_info()
    assert_db_init()
    
    if source:
        delete_source()
    elif media:
        delete_media()
    else:
        console.print(Panel("[bold red]Please specify either --media or --source option.[/bold red]", border_style="red"))

def delete_source():
    sources = session.query(Source).all()
    if not sources:
        console.print("[bold red]No sources available to delete.[/bold red]")
        return

    console.print("\n[bold green]Available Sources:[/bold green]")
    for index, source in enumerate(sources, start=1):
        console.print(f" {index}. {source.name} - {source.base_url}")
    console.print(" 0. Quit")

    while True:
        source_choice = Prompt.ask("[-] Select a source to delete by number or 0 to quit")
        if source_choice.isdigit():
            source_choice = int(source_choice)
            if source_choice == 0:
                console.print("[bold yellow]Quitting source delete process.[/bold yellow]")
                return
            elif 1 <= source_choice <= len(sources):
                selected_source = sources[source_choice - 1]
                break
            else:
                console.print("[bold red]Invalid choice. Please select a valid source number.[/bold red]")
        else:
            console.print("[bold red]Please enter a valid number.[/bold red]")

    # Check if there are media entries associated with the selected source
    associated_media_count = session.query(Media).filter_by(source_id=selected_source.id).count()
    if associated_media_count > 0:
        console.print(Panel(
            f"[bold yellow]Cannot delete source '{selected_source.name}' because it is associated with {associated_media_count} media entry/entries.[/bold yellow]",
            border_style="yellow"
        ))
        return

    try:
        session.delete(selected_source)
        session.commit()
        console.print(Panel("[bold green]Source deleted successfully.[/bold green]", border_style="green"))
    except Exception as e:
        session.rollback()
        console.print(Panel(f"[bold red]Error deleting source: {str(e)}[/bold red]", border_style="red"))


def delete_media():
    media_entries = session.query(Media).all()
    if not media_entries:
        console.print("[bold red]No media entries available to delete.[/bold red]")
        return

    console.print("\n[bold green]Available Media:[/bold green]")
    for index, media in enumerate(media_entries, start=1):
        console.print(f" {index}. {media.url} (Source ID: {media.source_id})")
    console.print(" 0. Quit")

    while True:
        media_choice = Prompt.ask("[-] Select a media to delete by number or 0 to quit")
        if media_choice.isdigit():
            media_choice = int(media_choice)
            if media_choice == 0:
                console.print("[bold yellow]Quitting media delete process.[/bold yellow]")
                return
            elif 1 <= media_choice <= len(media_entries):
                selected_media = media_entries[media_choice - 1]
                break
            else:
                console.print("[bold red]Invalid choice. Please select a valid media number.[/bold red]")
        else:
            console.print("[bold red]Please enter a valid number.[/bold red]")

    try:
        session.delete(selected_media)
        session.commit()
        console.print(Panel("[bold green]Media deleted successfully.[/bold green]", border_style="green"))
    except Exception as e:
        session.rollback()
        console.print(Panel(f"[bold red]Error deleting media: {str(e)}[/bold red]", border_style="red"))
