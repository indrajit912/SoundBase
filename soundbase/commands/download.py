# This script handles the download command.
# Author: Indrajit Ghosh
# Created On: Jan 03, 2025

import click
import os
import shutil
from uuid import UUID

from rich.panel import Panel
from rich.console import Console

from soundbase.db.database import session, local_session
from soundbase.db.models import Media, Source, SystemInfo
from soundbase.utils.db_utils import add_media_to_db, add_source_to_db
from soundbase.utils.cli_utils import assert_db_init, print_basic_info
from soundbase.utils.yt_dlp_utils import download_audio
from soundbase.config import DEFAULT_MEDIA_DIR, DATABASE_PATH

console = Console()

@click.group()
def download():
    """
    Download commands for:
    - Download media from source to a specified media directory
    - Download the soundbase database to a specified directory

    Available commands:
    - media: Download media by ID or URL
    - db: Download the soundbase database
    
    Example usage:
        $ soundbase download media -id "sdklfj-dfslkdkdfs-dsfkldsf-dfs"
        $ soundbase download media --url "http://example.com"       
        $ soundbase download media -all         # This will download all media

        $ soundbase download db --download_dir "/media/jellyfin"          
    """
    pass

@download.command()
@click.option('-id', '--media_id', type=str, help="ID of the media to download")
@click.option('-u', '--url', type=str, help="URL of the media to download")
@click.option('-dir', '--media_dir', type=str, help="Directory to save the downloaded media")
@click.option('-all', '--download_all', is_flag=True, help="Download all media from the database")
def media(media_id, url, media_dir, download_all):
    """
    Download media from the provided ID or URL.

    Downloads media by either media ID or URL. If a media directory is not specified, 
    it will use the default directory (DEFAULT_MEDIA_DIR).
    """
    # Ensure database is initialized and print basic info
    print_basic_info()
    assert_db_init()

    # Set the directory to download the media
    if not media_dir:
        # Get the media dir from db
        system_info = local_session.query(SystemInfo).first()
        media_dir = system_info.media_dir if system_info else DEFAULT_MEDIA_DIR

    if download_all:
        # Download all media from the Media table
        all_media = session.query(Media).all()

        if not all_media:
            console.print(Panel("No media found in the database.", style="bold red"))
            return

        console.print(Panel(f"Found {len(all_media)} media entries. Starting download...", style="bold green"))

        for media in all_media:
            try:
                console.print(f"Downloading: {media.title} ({media.id}) - {media.url}", style="bold blue")
                download_audio(url=media.url, output_path=media_dir)
            except Exception as e:
                console.print(Panel(f"Error downloading media '{media.title}': {e}", style="bold red"))
        
        console.print(f"All media downloaded successfully in {media_dir}.", style="bold green")
        return

    # Ensure only one of media_id or url is provided
    if not (media_id or url):
        console.print(Panel("Error: Please provide either media ID or URL to download media.", style="bold red"))
        return
    if media_id and url:
        console.print(Panel("Error: Please provide only one of media ID or URL, not both.", style="bold red"))
        return

    # If media_id is provided, retrieve media info from the database
    if media_id:
        try:
            # Ensure media_id is a UUID object
            if isinstance(media_id, str):
                media_id = UUID(media_id)

            # Query the Media table to get the media details using the media_id
            media = session.query(Media).filter_by(id=media_id).first()

            if media is None:
                console.print(Panel(f"Error: Media with ID {media_id} not found.", style="bold red"))
                return

            # Extract the URL from the retrieved media object
            url = media.url
            console.print(f"Found media: {media.title} ({media.id}) - {media.url}", style="bold green")
            
        except Exception as e:
            console.print(Panel(f"Error retrieving media details: {e}", style="bold red"))
            return

    # If url is provided directly, use that URL
    if url:
        console.print(f"Using provided URL: {url}", style="bold green")

        # Check if the URL exists in the Media table
        existing_media = session.query(Media).filter_by(url=url).first()

        if existing_media:
            console.print(Panel(f"The media is already in the database: {existing_media.title} ({existing_media.id})", style="bold blue"))
        else:
            # Check if the URL is a YouTube URL
            if "youtube.com" in url or "youtu.be" in url:
                console.print(Panel("This YouTube URL is not in the database.", style="bold yellow"))
                if click.confirm("Would you like to add this media to the database?"):
                    # Retrieve or create the YouTube source
                    youtube_source = session.query(Source).filter_by(base_url="https://www.youtube.com").first()
                    if not youtube_source:
                        add_source_to_db(session=session, name="YouTube", base_url="https://www.youtube.com")

                    # Ask the user for a title for the media
                    title = click.prompt("Please provide a title for the media", type=str)

                    # Add the media to the database
                    result = add_media_to_db(session=session, url=url, title=title, source_id=youtube_source.id)
                    if result["status"] == "success":
                        console.print(Panel(f"[bold green]Media added successfully:[/bold green] {result['media_title']}", border_style="green"))
                    else:
                        console.print(Panel(f"[bold red]Error adding media: {result['message']}[/bold red]", border_style="red"))


    # Perform the download
    download_audio(url=url, output_path=media_dir)

    console.print(f"Media download completed successfully in {media_dir}.", style="bold green")


@download.command()
@click.option('-dir', '--download_dir', type=str, help="Path to the directory to download the db.")
def db(download_dir):
    """
    Download the soundbase database to a specified directory.

    The database will be copied to the specified directory. If no directory is provided, 
    the default directory (~/Downloads) will be used.
    """
    # Ensure database is initialized and print basic info
    print_basic_info()
    assert_db_init()

    # Use the default download directory if not specified
    if not download_dir:
        download_dir = os.path.expanduser('~/Downloads')

    # Path to the soundbase database file
    db_path = DATABASE_PATH

    # Ensure the download directory exists
    if not os.path.exists(download_dir):
        console.print(Panel(f"Error: The directory {download_dir} does not exist.", style="bold red"))
        return

    # Copy the database to the specified directory
    try:
        shutil.copy(db_path, download_dir)
        console.print(f"Database successfully copied to {download_dir}.", style="bold green")
    except Exception as e:
        console.print(Panel(f"Error copying database: {e}", style="bold red"))
