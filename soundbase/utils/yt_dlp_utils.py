# soundbase/utils/yt_dlp_utils.py
# A script to use yt-dlp to download media from websites!
# Author: Indrajit Ghosh
# Created On: Jan 02, 2025
# 
import yt_dlp
from pathlib import Path

def download_audio(url, output_path):
    """
    Downloads the audio from a given YouTube URL, extracts it in MP3 format,
    embeds metadata, and adds a thumbnail if available, saving it to the specified path.

    Args:
        url (str): The YouTube video URL from which to download the audio.
        output_path (str or Path): The directory where the downloaded audio will be saved.

    Returns:
        None: Downloads the audio and saves it as a file in the specified directory.
        
    Postprocessing Options:
        - Converts audio to MP3 format with a preferred quality of 192 kbps.
        - Extracts and adds metadata to the audio file.
        - Embeds the video thumbnail in the audio file (if available).
    """
    # Convert the output_path to a Path object (if it's not already)
    output_path = Path(output_path)

    # Ensure the output path exists
    output_path.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio[ext=mp3]/best',  # Ensure the best audio quality in MP3 format
        'writethumbnail': True,  # Download thumbnail image
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),  # Specify the output path and filename template
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},  # Audio extraction to MP3
            {'key': 'FFmpegMetadata', 'add_metadata': 'True'},  # Add metadata to audio
            {'key': 'EmbedThumbnail', 'already_have_thumbnail': False},  # Embed thumbnail if not already present
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    dir = Path.home() / "Downloads"
    download_audio('https://www.youtube.com/watch?v=S9bCLPwzSC0', dir)

if __name__ == '__main__':
    main()
    

