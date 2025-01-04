# soundbase/utils/db_utils.py
# Author: Indrajit Ghosh
# Created On: Jan 02, 2025
#
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from soundbase.db.models import Source, Media, Album
from soundbase.utils.general_utils import sha256_hash

def add_source_to_db(session, name, base_url):
    """
    Adds a new Source to the database.

    Args:
        session (Session): The SQLAlchemy session object.
        name (str): The name of the source.
        base_url (str): The base URL of the source.

    Returns:
        dict: A dictionary containing the result of the add operation.
    """
    # Strip whitespace from the name
    name = name.strip()
    base_url = base_url.strip().rstrip('/') # Removing the end '/' from the url


    try:
        # Check if a source with the same base_url already exists
        existing_source = session.query(Source).filter_by(base_url=base_url).first()
        if existing_source:
            return {
                "status": "error",
                "message": f"A source with the base URL '{base_url}' already exists."
            }

        # Create a new source object
        source = Source(name=name, base_url=base_url)

        # Add the source object to the session and commit the transaction
        session.add(source)
        session.commit()

        # Return success message with the source ID
        return {
            "status": "success",
            "message": f"Source '{name}' has been added successfully.",
            "source_id": source.id,
            "source_name": source.name,
            "source_base_url": source.base_url
        }
    except SQLAlchemyError as e:
        session.rollback()  # Rollback the transaction in case of error
        return {
            "status": "error",
            "message": f"An error occurred while adding the source: {str(e)}"
        }


def add_media_to_db(session, url, title, source_id, album_ids=None):
    """
    Adds a new Media entry to the database and optionally associates it with one or more albums.

    Args:
        session (Session): The SQLAlchemy session object.
        url (str): The URL of the media.
        title (str): The title of the media.
        source_id (UUID): The ID of the associated source.
        album_ids (list[str], optional): List of album IDs (as strings) to associate with the media.

    Returns:
        dict: A dictionary containing the result of the add operation.
    """
    title = title.strip()
    url = url.strip().rstrip('/')
    
    try:
        # Convert album_ids to UUIDs
        album_uuids = []
        if album_ids:
            try:
                album_uuids = [UUID(album_id) for album_id in album_ids]
            except ValueError:
                return {
                    "status": "error",
                    "message": "One or more album IDs are not valid UUIDs."
                }

        # Check for duplicate media
        existing_media = session.query(Media).filter_by(url=url).first()
        if existing_media:
            return {
                "status": "error",
                "message": f"A media entry with the URL '{url}' already exists."
            }

        # Create the media object
        media = Media(url=url, title=title, source_id=source_id)

        # Associate media with albums if album IDs are provided
        if album_uuids:
            albums = session.query(Album).filter(Album.id.in_(album_uuids)).all()
            if not albums or len(albums) != len(album_uuids):
                return {
                    "status": "error",
                    "message": "One or more album IDs are invalid."
                }
            media.albums.extend(albums)

        # Add the media to the session and commit
        session.add(media)
        session.commit()

        return {
            "status": "success",
            "message": f"Media '{title}' has been added successfully.",
            "media_id": media.id,
            "media_title": media.title,
            "media_url": media.url,
            "media_albums": [album.id for album in media.albums]
        }
    except SQLAlchemyError as e:
        session.rollback()
        return {
            "status": "error",
            "message": f"An error occurred while adding the media: {str(e)}"
        }


def add_album_to_db(session, name: str, media_ids: list = None):
    """
    Adds a new Album entry to the database, optionally associating media entries.

    Args:
        session (Session): The SQLAlchemy session object.
        name (str): The name of the album.
        media_ids (list): A list of UUIDs (as strings) representing media entries to associate with the album.

    Returns:
        dict: A dictionary containing the result of the add operation.
    """
    name = name.strip()

    try:
        # Check if the album already exists
        existing_album = session.query(Album).filter_by(name=name).first()
        if existing_album:
            return {
                "status": "error",
                "message": f"An album with the name '{name}' already exists."
            }

        # Convert media_ids to UUIDs
        media_uuids = []
        if media_ids:
            try:
                media_uuids = [UUID(media_id) for media_id in media_ids]
            except ValueError:
                return {
                    "status": "error",
                    "message": "One or more media IDs are not valid UUIDs."
                }

        # Create the album
        album = Album(name=name)

        # Associate media entries if media IDs are provided
        if media_uuids:
            media_entries = session.query(Media).filter(Media.id.in_(media_uuids)).all()
            if len(media_entries) != len(media_uuids):
                missing_ids = set(media_uuids) - {media.id for media in media_entries}
                return {
                    "status": "error",
                    "message": f"Some media entries were not found: {missing_ids}"
                }
            album.media.extend(media_entries)

        # Add the album to the session and commit
        session.add(album)
        session.commit()

        return {
            "status": "success",
            "message": f"Album '{name}' has been added successfully.",
            "album_id": album.id,
            "album_name": album.name,
            "associated_media_ids": [media.id for media in album.media]
        }
    except SQLAlchemyError as e:
        session.rollback()
        return {
            "status": "error",
            "message": f"An error occurred while adding the album: {str(e)}"
        }

def delete_media_from_db(session, media_id):
    """
    Deletes a media entry from the database by its ID.
    
    Parameters:
    - session (Session): The SQLAlchemy session to interact with the database.
    - media_id (UUID): The ID of the media entry to delete.
    
    Returns:
    - dict: A dictionary containing the result of the delete operation.
    """
    # Ensure source_id is a UUID object
    if isinstance(media_id, str):
        media_id = UUID(media_id)

    # Query the Media object by ID
    media = session.query(Media).filter_by(id=media_id).first()
    
    if media:
        try:
            # Delete the media object
            session.delete(media)
            session.commit()  # Commit the transaction
            
            # Return success message
            return {
                "status": "success",
                "message": f"Media entry with ID {media_id} has been deleted.",
                "media_id": media_id
            }
        
        except SQLAlchemyError as e:
            session.rollback()  # Rollback the transaction in case of error
            return {
                "status": "error",
                "message": f"An error occurred while deleting the media entry: {str(e)}"
            }
    
    else:
        return {
            "status": "error",
            "message": f"No media found with ID {media_id}."
        }
    
def delete_source_from_db(session, source_id):
    """
    Deletes a source entry from the database by its ID.
    
    Parameters:
    - session (Session): The SQLAlchemy session to interact with the database.
    - source_id (UUID): The ID of the source entry to delete.
    
    Returns:
    - dict: A dictionary containing the result of the delete operation.
    """
    # Ensure source_id is a UUID object
    if isinstance(source_id, str):
        source_id = UUID(source_id)

    # Query the Source object by ID
    source = session.query(Source).filter_by(id=source_id).first()
    
    if source:
        # Check if there are media entries associated with the selected source
        associated_media_count = session.query(Media).filter_by(source_id=source_id).count()
        if associated_media_count > 0:
            return {
                "status": "error",
                "message": f"Cannot delete source '{source.name}' because it is associated with {associated_media_count} media entry/entries."
            }
        else:
            try:
                # Delete the source object
                session.delete(source)
                session.commit()  # Commit the transaction

                # Return success message
                return {
                    "status": "success",
                    "message": f"Source entry with ID {source_id} has been deleted.",
                    "source_id": source_id
                }

            except SQLAlchemyError as e:
                session.rollback()  # Rollback the transaction in case of error
                return {
                    "status": "error",
                    "message": f"An error occurred while deleting the source entry: {str(e)}"
                }
    
    else:
        return {
            "status": "error",
            "message": f"No source found with ID {source_id}."
        }

def update_media_in_db(session, media_id, title: str = None, url: str = None, source_id=None, album_ids: list = None):
    """
    Updates an existing media entry in the database.
    
    Parameters:
    - session (Session): The SQLAlchemy session to interact with the database.
    - media_id (UUID): The ID of the media entry to update.
    - title (str, optional): The new title of the media (if provided).
    - url (str, optional): The new URL of the media (if provided).
    - source_id (UUID, optional): The new source ID for the media (if provided).
    - album_ids (list, optional): A list of UUIDs representing album entries to associate with the media.
    
    Returns:
    - dict: A dictionary containing the result of the update operation.
    """
    # Ensure media_id is a UUID object
    if isinstance(media_id, str):
        media_id = UUID(media_id)
    
    # Ensure source_id is a UUID object
    if source_id and isinstance(source_id, str):
        source_id = UUID(source_id)
    
    # Ensure album_ids are UUID objects
    if album_ids:
        album_ids = [UUID(album_id) if isinstance(album_id, str) else album_id for album_id in album_ids]

    # Query the Media object by ID
    media = session.query(Media).filter_by(id=media_id).first()
    
    if media:
        try:
            # Update fields if the new values are provided
            updated_fields = {}
            if title:
                media.title = title.strip()
                updated_fields["title"] = title.strip()
            if url:
                media.url = url.strip().rstrip('/')
                media.hash = sha256_hash(url)  # Recalculate hash if URL is updated
                updated_fields["url"] = url.strip().rstrip('/')
            if source_id:
                media.source_id = source_id
                updated_fields["source_id"] = source_id
            if album_ids:
                # Query the albums by ID
                albums = session.query(Album).filter(Album.id.in_(album_ids)).all()
                if len(albums) != len(album_ids):
                    missing_ids = set(album_ids) - {album.id for album in albums}
                    return {
                        "status": "error",
                        "message": f"Some album entries were not found: {missing_ids}"
                    }
                media.albums = albums  # Update the relationship
                updated_fields["album_ids"] = [album.id for album in albums]

            # Commit the changes
            session.commit()
            
            # Return success message with updated fields
            return {
                "status": "success",
                "message": f"Media entry with ID {media_id} has been updated.",
                "updated_fields": updated_fields,
                "media": media.json()
            }
        
        except SQLAlchemyError as e:
            session.rollback()  # Rollback the transaction in case of error
            return {
                "status": "error",
                "message": f"An error occurred while updating the media entry: {str(e)}"
            }
    
    else:
        return {
            "status": "error",
            "message": f"No media found with ID {media_id}."
        }

def update_album_in_db(session, album_id, name: str = None, media_ids: list = None):
    """
    Updates an existing album entry in the database.
    
    Parameters:
    - session (Session): The SQLAlchemy session to interact with the database.
    - album_id (UUID): The ID of the album entry to update.
    - name (str, optional): The new name of the album (if provided).
    - media_ids (list, optional): A list of UUIDs representing media entries to associate with the album.
    
    Returns:
    - dict: A dictionary containing the result of the update operation.
    """
    # Ensure album_id is a UUID object
    if isinstance(album_id, str):
        album_id = UUID(album_id)
    
    # Ensure media_ids are UUID objects
    if media_ids:
        media_ids = [UUID(media_id) if isinstance(media_id, str) else media_id for media_id in media_ids]

    # Query the Album object by ID
    album = session.query(Album).filter_by(id=album_id).first()
    
    if album:
        try:
            # Update fields if the new values are provided
            updated_fields = {}
            if name:
                album.name = name.strip()
                updated_fields["name"] = name.strip()
            if media_ids:
                # Query the media by ID
                media = session.query(Media).filter(Media.id.in_(media_ids)).all()
                if len(media) != len(media_ids):
                    missing_ids = set(media_ids) - {m.id for m in media}
                    return {
                        "status": "error",
                        "message": f"Some media entries were not found: {missing_ids}"
                    }
                album.media = media  # Update the relationship
                updated_fields["media_ids"] = [m.id for m in media]

            # Commit the changes
            session.commit()
            
            # Return success message with updated fields
            return {
                "status": "success",
                "message": f"Album entry with ID {album_id} has been updated.",
                "updated_fields": updated_fields,
                "album": album.json()
            }
        
        except SQLAlchemyError as e:
            session.rollback()  # Rollback the transaction in case of error
            return {
                "status": "error",
                "message": f"An error occurred while updating the album entry: {str(e)}"
            }
    
    else:
        return {
            "status": "error",
            "message": f"No album found with ID {album_id}."
        }


def update_source_in_db(session, source_id, name: str = None, base_url: str = None):
    """
    Updates an existing source entry in the database.
    
    Parameters:
    - session (Session): The SQLAlchemy session to interact with the database.
    - source_id (UUID): The ID of the source entry to update.
    - name (str, optional): The new name of the source (if provided).
    - base_url (str, optional): The new base URL of the source (if provided).
    
    Returns:
    - dict: A dictionary containing the result of the update operation.
    """
    # Ensure source_id is a UUID object
    if isinstance(source_id, str):
        source_id = UUID(source_id)

    # Query the Source object by ID
    source = session.query(Source).filter_by(id=source_id).first()
    
    if source:
        try:
            # Update fields if the new values are provided
            updated_fields = {}
            if name:
                source.name = name.strip()
                updated_fields["name"] = name.strip()
            if base_url:
                source.base_url = base_url.strip().rstrip('/')
                updated_fields["base_url"] = base_url.strip().rstrip('/')
            
            # Commit the changes
            session.commit()
            
            # Return success message with updated fields
            return {
                "status": "success",
                "message": "Source entry updated successfully",
                "updated_fields": updated_fields,
                "source": source.json()
            }
        
        except SQLAlchemyError as e:
            session.rollback()  # Rollback the transaction in case of error
            return {
                "status": "error",
                "message": f"An error occurred while updating the source entry: {str(e)}"
            }
    
    else:
        return {
            "status": "error",
            "message": f"No source found with ID {source_id}."
        }

def search_media_in_db(session, title: str = None, url: str = None, source_id=None):
    """
    Searches for media entries in the database based on the given filters.

    Args:
        session (Session): The SQLAlchemy session object.
        title (str, optional): The title of the media to search for.
        url (str, optional): The URL of the media to search for.
        source_id (UUID, optional): The source ID associated with the media to search for.

    Returns:
        dict: A dictionary containing the search results or an error message.
    """
    try:
        # Start the query
        query = session.query(Media)
        
        # Apply filters if provided
        if title:
            query = query.filter(Media.title.ilike(f"%{title.strip()}%"))
        if url:
            query = query.filter(Media.url.ilike(f"%{url.strip()}%"))
        if source_id:
            if isinstance(source_id, str):
                source_id = UUID(source_id)
            query = query.filter(Media.source_id == source_id)
        
        # Execute the query and fetch all matching results
        results = query.all()

        # Check if any results were found
        if results:
            return {
                "status": "success",
                "message": f"Found {len(results)} media entry/entries matching the criteria.",
                "media": [media.json() for media in results]  # Assuming Media model has a `json` method
            }
        else:
            return {
                "status": "success",
                "message": "No media entries found matching the criteria.",
                "media": []
            }
    except SQLAlchemyError as e:
        return {
            "status": "error",
            "message": f"An error occurred while searching for media entries: {str(e)}"
        }

def search_source_in_db(session, source_name: str = None, source_id: str = None, base_url: str = None):
    """
    Searches for source entries in the database based on the given filters.

    Args:
        session (Session): The SQLAlchemy session object.
        source_name (str, optional): The name of the source to search for.
        source_id (str, optional): The source ID to search for.
        base_url (str, optional): The base URL of the source to search for.

    Returns:
        dict: A dictionary containing the search results or an error message.
    """
    try:
        # Start the query
        query = session.query(Source)
        
        # Apply filters if provided
        if source_name:
            query = query.filter(Source.name.ilike(f"%{source_name.strip()}%"))
        if source_id:
            if isinstance(source_id, str):
                source_id = UUID(source_id)
            query = query.filter(Source.id == source_id)
        if base_url:
            query = query.filter(Source.base_url.ilike(f"%{base_url.strip()}%"))
        
        # Execute the query and fetch all matching results
        results = query.all()

        # Check if any results were found
        if results:
            return {
                "status": "success",
                "message": f"Found {len(results)} source entry/entries matching the criteria.",
                "sources": results  # Return the source objects themselves
            }
        else:
            return {
                "status": "success",
                "message": "No source entries found matching the criteria.",
                "sources": []
            }
    except SQLAlchemyError as e:
        return {
            "status": "error",
            "message": f"An error occurred while searching for source entries: {str(e)}"
        }
