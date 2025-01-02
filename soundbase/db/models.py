# db/models.py
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025
#
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, validates
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from soundbase.config import DATABASE_URL
from soundbase.utils.general_utils import utcnow, sha256_hash, convert_utc_to_local_str

Base = declarative_base()

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
    __tablename__ = 'sources'

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

        console.print(Panel(table, title=f"{count_display}{self.id}", title_align="left", border_style="bright_blue"))

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
    source_id = Column(UUID(as_uuid=True), ForeignKey('sources.id'), nullable=False)  # Foreign key to Source
    added_on = Column(DateTime, default=utcnow)  # Timestamp when the media was added
    last_modified = Column(DateTime, default=utcnow, onupdate=utcnow)  # Last modification timestamp

    source = relationship("Source", back_populates="media")  # Establishes a relationship with Source

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

        console.print(Panel(table, title=f"{count_display}{self.id}", title_align="left", border_style="bright_blue"))

# Create an engine and session for interacting with the database
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create a session
session = Session()
