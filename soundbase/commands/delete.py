# This script handles the del command.
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025
#
# TODO: Modify this command to include subcommands.
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from soundbase.db.database import session
from soundbase.utils.cli_utils import assert_db_init, print_basic_info
from soundbase.utils.db_utils import delete_media_from_db, delete_source_from_db

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
            $ soundbase del --source

        To delete a media entry:
            $ soundbase del --media

    Notes:
        - Deleting a source is not allowed if it is associated with any media entries.
        - If neither `--source` nor `--media` is provided, the command will prompt the user 
          to specify one of the options.
    """
    print_basic_info()
    assert_db_init()

    if source:
        source_id = Prompt.ask("[bold cyan]Enter the Source ID to delete[/bold cyan]")
        result = delete_source_from_db(session, source_id)
        if result["status"] == "success":
            console.print(Panel(f"[bold green]{result['message']}[/bold green]", border_style="green"))
        else:
            console.print(Panel(f"[bold red]{result['message']}[/bold red]", border_style="red"))
    elif media:
        media_id = Prompt.ask("[bold cyan]Enter the Media ID to delete[/bold cyan]")
        result = delete_media_from_db(session, media_id)
        if result["status"] == "success":
            console.print(Panel(f"[bold green]{result['message']}[/bold green]", border_style="green"))
        else:
            console.print(Panel(f"[bold red]{result['message']}[/bold red]", border_style="red"))
    else:
        console.print(Panel("[bold red]Please specify either --media or --source option.[/bold red]", border_style="red"))

