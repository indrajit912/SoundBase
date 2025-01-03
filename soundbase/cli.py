# cli.py - Main entry point for the CLI.
import click
from rich.console import Console
from rich.panel import Panel

from soundbase.commands import init, add, add_source, list, delete, local, search, download, update
from soundbase.utils.cli_utils import print_basic_info

console = Console()

@click.command()
def help():
    """Displays help about the available commands."""
    print_basic_info()
    console.print(Panel("Help - SoundBase CLI", style="green", title="Command List"))

    for command_name, command in cli.commands.items():
        if command is not help:  # Skip displaying help for the help command itself
            console.print(f"\n[bold yellow]{command_name}[/bold yellow]: {command.help}")

@click.group()
def cli():
    pass

# Add commands to the group
cli.add_command(init.init)
cli.add_command(help, name='help')
cli.add_command(add.add)
cli.add_command(add_source.add_source)
cli.add_command(list.list)
cli.add_command(search.search)
cli.add_command(update.update)
cli.add_command(delete.delete, name="del")
cli.add_command(download.download)
cli.add_command(local.local)

if __name__ == '__main__':
    cli()