# main.py
# Author: Indrajit Ghosh
# Created On: Jan 01, 2024
#
# This project helps me to create and manage my music database
# It collects various musics and their urls and save it to the 
# sqlite3 database locally
#
from db.database import init_db
from db.models import Music, Source
from utils.downloader import download_music

if __name__ == "__main__":
    init_db()  # Initialize the database

    # Add a new source
    source = Source(name="YouTube", base_url="https://www.youtube.com")
    
    # Add music (you can call a function to fetch from the source)
    music_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    music = Music(url=music_url, source=source)
    
    # For now, simply print out all music
    print(f"Music URL: {music.url}, Source: {music.source.name}")
