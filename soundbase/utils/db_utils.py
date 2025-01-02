# soundbase/utils/db_utils.py
# Author: Indrajit Ghosh
# Created On: Jan 02, 2025
#
from soundbase.db.models import Source, Media

def add_source_to_db(session, name, base_url):
    """
    Adds a new Source to the database.

    Args:
        session (Session): The SQLAlchemy session object.
        name (str): The name of the source.
        base_url (str): The base URL of the source.

    Returns:
        Source: The newly created Source object.
    """
    # Strip whitespace from the name
    name = name.strip()
    
    source = Source(name=name, base_url=base_url)
    session.add(source)
    session.commit()
    return source

def add_media_to_db(session, url, title, source_id):
    """
    Adds a new Media entry to the database.

    Args:
        session (Session): The SQLAlchemy session object.
        url (str): The URL of the media.
        title (str): The title of the media.
        source_id (UUID): The ID of the associated source.

    Returns:
        Media: The newly created Media object.
    """
    # Strip whitespace from the title
    title = title.strip()

    media = Media(url=url, title=title, source_id=source_id)
    session.add(media)
    session.commit()
    return media
