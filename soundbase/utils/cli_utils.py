
import os
import sys
from datetime import date

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from sqlalchemy import inspect

from soundbase.version import __version__
from soundbase.db.database import local_engine, engine
from soundbase.config import APP_NAME, COPYRIGHT_STATEMENT, GITHUB_REPO

console = Console()

def clear_terminal_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to print basic information
def print_basic_info():

    clear_terminal_screen()

    # Create title with centered alignment
    title = Panel(f"{APP_NAME} - SoundBase App\nGitHub: {GITHUB_REPO}", title=f"{APP_NAME}", title_align="center", style="bold white on blue", border_style="bright_blue")

    # Create information table with centered alignment
    info_table = Table(show_header=False)
    info_table.add_row("[center]Version[/center]", f"[center]{__version__}[/center]")
    info_table.add_row("[center]Copyright[/center]", f"[center]{COPYRIGHT_STATEMENT}[/center]")
    info_table.add_row("[center]Today's Date[/center]", f"[center]{date.today().strftime('%B %d, %Y')}[/center]")

    # Print title and information table
    console.print(title)
    console.print(info_table)
    console.print("\n")


def check_db_init():
    """
    Check if the local database has been initialized.
    
    This function checks whether the `SystemInfo` table exists in the local database.
    If the table exists, it means the app has been initialized. Otherwise, it has not.
    
    Returns:
        bool: True if the database has been initialized, False otherwise.
    """
    try:
        # Check if the SystemInfo table exists in the local database
        if inspect(local_engine).has_table('system_info'):
            return True
        else:
            return False
    except Exception as e:
        return False


def assert_db_init():
    # Check db_init
    if not check_db_init():
        console.print(Panel("[red]No database found![/red] The app is probably not initialized yet.", title="Error", style="bold red"))
        console.print("Please use the [bold]`init`[/bold] command to initialize the app.", style="yellow")
        sys.exit(1)