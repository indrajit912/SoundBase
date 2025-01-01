# db/models.py
# Author: Indrajit Ghosh
# Created On: Jan 01, 2025
#
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from soundbase.config import DATABASE_URL
from soundbase.utils.general_utils import utcnow

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
            "source_id": str(self.source_id),
            "added_on": self.added_on.isoformat(),
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "source": self.source.json()  # Include the source information in the JSON response
        }

# Create an engine and session for interacting with the database
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create a session
session = Session()
