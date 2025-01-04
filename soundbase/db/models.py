# db/models.py
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025
#
import uuid
import os
import shutil
import psutil
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy import Table as SQLAlchemyTable
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from soundbase.db.database import Base, LocalBase
from soundbase.utils.general_utils import utcnow, sha256_hash, convert_utc_to_local_str
from soundbase.config import DEFAULT_MEDIA_DIR, DATABASE_PATH

class Source(Base):
    """
    Represents a source website for media (music or video) downloads.
    
    Attributes:
        id (UUID): The unique identifier for the source.
        name (str): The name of the source website.
        base_url (str): The base URL of the source website.
        created_on (datetime): Timestamp of when the source was created.
        last_modified (datetime): Timestamp of when the source was last modified.

    Relationships:
        media (relationship): A one-to-many relationship with the Media model.
    """
    __tablename__ = 'source'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)  # Website name
    base_url = Column(String, nullable=False, unique=True)  # Base URL of the source website
    created_on = Column(DateTime, default=utcnow)  # Timestamp of creation
    last_modified = Column(DateTime, default=utcnow, onupdate=utcnow)  # Last modification timestamp

    media = relationship("Media", back_populates="source")  # Establishes a relationship with Media

    def __repr__(self):
        return f"<Source(name={self.name}, base_url={self.base_url})>"

    def json(self):
        """
        Converts the Source instance into a JSON-compatible dictionary.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "base_url": self.base_url,
            "created_on": self.created_on.isoformat(),
            "last_modified": self.last_modified.isoformat() if self.last_modified else None
        }
    
    def print_on_screen(self, count=None):
        """
        Prints the Source information on the terminal screen in a professional CLI app style using the rich library.
        """
        console = Console()

        count_display = f"({count}) " if count else ''  # Handle the count parameter

        table = Table(title="Source Details", title_style="bold cyan", style="bright_blue")
        table.add_column("Field", style="bold white", width=16)
        table.add_column("Value", justify="left", style="bright_yellow")

        # Add rows with colors for each field
        table.add_row("ID", f"[green]{str(self.id)}[/green]")
        table.add_row("Name", f"[magenta]{self.name}[/magenta]")
        table.add_row("Base URL", f"[cyan]{self.base_url}[/cyan]")

        dt_created_iso = self.created_on.isoformat()
        dt_created_str = convert_utc_to_local_str(datetime.fromisoformat(dt_created_iso))
        table.add_row("Created On", f"[purple]{dt_created_str}[/purple]")

        dt_last_modified_iso = self.last_modified.isoformat()
        dt_last_modified_str = convert_utc_to_local_str(datetime.fromisoformat(dt_last_modified_iso))
        table.add_row("Last Modified", f"[purple]{dt_last_modified_str}[/purple]")

        console.print(Panel(table, title=f"{count_display}{self.name}", title_align="left", border_style="bright_blue"))

# Define the association table for the many-to-many relationship
album_media_association = SQLAlchemyTable(
    "album_media",
    Base.metadata,
    Column("album_id", UUID(as_uuid=True), ForeignKey("album.id"), primary_key=True),
    Column("media_id", UUID(as_uuid=True), ForeignKey("media.id"), primary_key=True)
)

class Album(Base):
    """
    Represents an album containing media entries (music or video).
    
    Attributes:
        id (UUID): The unique identifier for the album.
        name (str): The name of the album.
        created_on (datetime): Timestamp of when the album was created.
        last_modified (datetime): Timestamp of when the album was last modified.

    Relationships:
        media (relationship): A many-to-many relationship with the Media model.
    """
    __tablename__ = 'album'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique UUID for each album
    name = Column(String(100), nullable=False, unique=True)  # Name of the album
    created_on = Column(DateTime, default=utcnow)  # Timestamp of creation
    last_modified = Column(DateTime, default=utcnow, onupdate=utcnow)  # Last modification timestamp

    media = relationship("Media", secondary=album_media_association, back_populates="albums")  # Relationship with Media

    def __repr__(self):
        return f"<Album(id={self.id}, name={self.name})>"

    def json(self):
        """
        Converts the Album instance into a JSON-compatible dictionary.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "created_on": self.created_on.isoformat(),
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "media": [m.id for m in self.media]  # List of associated media IDs
        }
    
    def print_on_screen(self, count=None):
        """
        Prints the details of the Album instance on the screen in a structured format.

        Args:
            count (int, optional): A number to display as an index for the album.
        """
        console = Console()

        # Create a Rich table to display album details
        table = Table(title=f"Album {count}: {self.name}" if count else f"Album: {self.name}", style="cyan")
        table.add_column("Field", style="bold magenta", justify="right")
        table.add_column("Value", style="white", justify="left")

        # Add album details to the table
        table.add_row("ID", str(self.id))
        table.add_row("Name", self.name)
        created_on_iso = self.created_on.isoformat()
        created_on_str = convert_utc_to_local_str(datetime.fromisoformat(created_on_iso))
        table.add_row("Created On", created_on_str)
        last_modified_iso = self.last_modified.isoformat()
        last_modified_str = convert_utc_to_local_str(datetime.fromisoformat(last_modified_iso))
        table.add_row("Last Modified", last_modified_str)

        # Add associated media IDs
        if self.media:
            media_ids = "\n".join([str(m.id) for m in self.media])
            table.add_row("Media", media_ids)
        else:
            table.add_row("Media", "No media associated")

        # Display the table using Rich
        console.print(Panel(table, title=f"Album {count}" if count else "Album Details", border_style="green"))


class Media(Base):
    """
    Represents a media entry (music or video) in the database.
    
    Attributes:
        id (UUID): The unique identifier for the media.
        url (str): The URL of the media (music or video).
        source_id (UUID): The foreign key referencing the source from which the media was obtained.
        added_on (datetime): Timestamp of when the media was added.
        last_modified (datetime): Timestamp of when the media was last modified.

    Relationships:
        source (relationship): A many-to-one relationship with the Source model.
    """
    __tablename__ = 'media'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique UUID for each media entry
    url = Column(Text, nullable=False, unique=True)  # URL of the media (music or video)
    title = Column(String(100), nullable=False) # Title of the media
    hash = Column(Text, nullable=False, unique=True)  # SHA-256 hash of the URL
    source_id = Column(UUID(as_uuid=True), ForeignKey('source.id'), nullable=False)  # Foreign key to Source
    added_on = Column(DateTime, default=utcnow)  # Timestamp when the media was added
    last_modified = Column(DateTime, default=utcnow, onupdate=utcnow)  # Last modification timestamp

    source = relationship("Source", back_populates="media")  # Establishes a relationship with Source
    albums = relationship("Album", secondary=album_media_association, back_populates="media")  # Relationship with Album

    def __repr__(self):
        return f"<Media(id={self.id}, url={self.url}, source={self.source.name})>"

    def json(self):
        """
        Converts the Media instance into a JSON-compatible dictionary.
        """
        return {
            "id": str(self.id),
            "url": self.url,
            "title": self.title,
            "source_id": str(self.source_id),
            "added_on": self.added_on.isoformat(),
            "albums": [album.id for album in self.albums],  # List of associated album IDs
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "source": self.source.json()  # Include the source information in the JSON response
        }
    
    @validates('url')
    def validate_url(self, key, value):
        """
        Validates and sets the hash of the URL when the URL is added or modified.
        """
        self.hash = sha256_hash(value)
        return value
    
    def print_on_screen(self, count=None):
        """
        Prints the Media information on the terminal screen in a professional CLI app style using the rich library.

        Parameters:
        count (int): Optional count to be displayed in the title (e.g., "(1)").
        """
        console = Console()

        count_display = f"({count}) " if count else ''  # Handle the count parameter

        table = Table(title="Media Details", title_style="bold cyan", style="bright_blue")
        table.add_column("Field", style="bold white", width=16)
        table.add_column("Value", justify="left", style="bright_yellow")

        # Add rows with colors for each field
        table.add_row("ID", f"[green]{str(self.id)}[/green]")
        table.add_row("Title", f"[magenta]{self.title}[/magenta]")
        table.add_row("URL", f"[cyan]{self.url}[/cyan]")
        table.add_row("Hash", f"[bright_green]{self.hash}[/bright_green]")

        added_on_iso = self.added_on.isoformat()
        added_on_str = convert_utc_to_local_str(datetime.fromisoformat(added_on_iso))
        table.add_row("Added On", f"[purple]{added_on_str}[/purple]")

        last_modified_iso = self.last_modified.isoformat()
        last_modified_str = convert_utc_to_local_str(datetime.fromisoformat(last_modified_iso))
        table.add_row("Last Modified", f"[purple]{last_modified_str}[/purple]")

        # Fetching the associated source information
        source = self.source
        table.add_row("Source Name", f"[bold yellow]{source.name}[/bold yellow]")
        table.add_row("Source ID", f"[bright_white]{str(self.source_id)}[/bright_white]")
        table.add_row("Source Base URL", f"[bright_cyan]{source.base_url}[/bright_cyan]")

        # Add albums row
        if self.albums:
            album_names = ", ".join(f"[bold magenta]{album.name}[/bold magenta]" for album in self.albums)
            table.add_row("Albums", album_names)
        else:
            table.add_row("Albums", "[italic bright_red]No associated albums[/italic bright_red]")


        console.print(Panel(table, title=f"{count_display}{self.id}", title_align="left", border_style="bright_blue"))

class SystemInfo(LocalBase):
    __tablename__ = 'system_info'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, default=os.getlogin)  # Default to the current system username
    installation_date = Column(DateTime, default=utcnow)   # Default to the current UTC time
    media_dir = Column(String, nullable=False, default=DEFAULT_MEDIA_DIR.__str__())  # Default to a placeholder directory
    soundbase_db = Column(String, nullable=False, default=DATABASE_PATH.__str__())
    last_modified = Column(DateTime, default=utcnow, onupdate=utcnow)  # Last modification timestamp

    os_type = Column(String, nullable=False, default=os.uname().sysname)
    os_version = Column(String, nullable=False, default=os.uname().release)
    architecture = Column(String, nullable=False, default=os.uname().machine)

    total_disk_space = Column(Integer, nullable=False, default=shutil.disk_usage("/").total)
    used_disk_space = Column(Integer, nullable=False, default=shutil.disk_usage("/").used)
    free_disk_space = Column(Integer, nullable=False, default=shutil.disk_usage("/").free)
    
    total_memory = Column(Integer, nullable=False, default=psutil.virtual_memory().total)
    used_memory = Column(Integer, nullable=False, default=psutil.virtual_memory().used)
    free_memory = Column(Integer, nullable=False, default=psutil.virtual_memory().available)
    

    @validates('media_dir')
    def validate_media_dir(self, key, value):
        if not os.path.isdir(value):
            raise ValueError(f"The directory '{value}' does not exist.")
        return value
    
    def __repr__(self):
        return f"<SystemInfo(username={self.username}, installation_date={self.installation_date}, media_dir={self.media_dir})>"
    
    def print_on_screen(self, count=None):
        """
        Prints the system information on the terminal screen in a professional CLI app style using the rich library.

        Parameters:
        count (int): Optional count to be displayed in the title (e.g., "(1)").
        """
        console = Console()

        count_display = f"({count}) " if count else ''  # Handle the count parameter

        # Create a table to display system information
        table = Table(title="Local System Information", title_style="bold cyan", style="bright_blue")
        table.add_column("Field", style="bold white", width=16)
        table.add_column("Value", justify="left", style="bright_yellow")

        # Add rows with colors for each field
        table.add_row("Username", f"[green]{self.username}[/green]")
        installation_dt_iso = self.installation_date.isoformat()
        installation_dt_str = convert_utc_to_local_str(datetime.fromisoformat(installation_dt_iso))
        table.add_row("App Installation Date", f"[magenta]{installation_dt_str}[/magenta]")
        table.add_row("Media Directory", f"[cyan]{self.media_dir}[/cyan]")
        table.add_row("SoundBase DB", f"[cyan]{self.soundbase_db}[/cyan]")

        last_modified_iso = self.last_modified.isoformat()
        last_modified_str = convert_utc_to_local_str(datetime.fromisoformat(last_modified_iso))
        table.add_row("Last Modified", f"[purple]{last_modified_str}[/purple]")

        # Add OS-related information
        table.add_row("OS Type", f"[yellow]{self.os_type}[/yellow]")
        table.add_row("OS Version", f"[yellow]{self.os_version}[/yellow]")
        table.add_row("Architecture", f"[yellow]{self.architecture}[/yellow]")

        # Add Disk space information (in GB)
        table.add_row("Total Disk Space", f"[bold green]{self.total_disk_space / (1024 ** 3):.2f} GB[/bold green]")
        table.add_row("Used Disk Space", f"[bold red]{self.used_disk_space / (1024 ** 3):.2f} GB[/bold red]")
        table.add_row("Free Disk Space", f"[bold yellow]{self.free_disk_space / (1024 ** 3):.2f} GB[/bold yellow]")

        # Add Memory information (in GB)
        table.add_row("Total Memory", f"[bold green]{self.total_memory / (1024 ** 3):.2f} GB[/bold green]")
        table.add_row("Used Memory", f"[bold red]{self.used_memory / (1024 ** 3):.2f} GB[/bold red]")
        table.add_row("Free Memory", f"[bold yellow]{self.free_memory / (1024 ** 3):.2f} GB[/bold yellow]")

        # Print the table in a panel
        console.print(Panel(table, title=f"{count_display}Local Info", title_align="left", border_style="bright_blue"))
