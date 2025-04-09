import argparse
import log
import os
# load the libraries that we'll use
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3
import mutagen.id3
from mutagen.id3 import ID3, TIT2, TIT3, TALB, TPE1, TRCK, TYER
from pathlib import Path
import json
from pydub import AudioSegment
from mutagen.id3 import ID3, ID3NoHeaderError

import glob

# import numpy as np

from metadata import Metadata
# smb://melnas._smb._tcp.local/melnas/iTunes/Music
# /Volumes/melnas/iTunes/Music
# /dev/disk4

log = log.setup_logger()
def main():
    
    parser = argparse.ArgumentParser(description="Music Library Organizer")
    parser.add_argument(
        "--music-path",
        "-mp",
        dest="music_path",
        default="/Volumes/melnas/iTunes/Music",
        help="Path to traverse for music files"
    )
    parser.add_argument(
        "--output-path",
        "-op",
        dest="output_path",
        default="/Volumes/USB_MUSIC",
        help="Path to the output directory"
    )
    parser.add_argument(
        "--excluded",
        nargs="+",
        default=["White Noise", "Audiobooks", "Podcasts", ".DS_Store", "Calming Water Consort", "The Yoga Masters", ".Media Preferences.plist"],
        dest="excluded",
        help="List of directories to exclude"
    )
    parser.add_argument(
        "--music-set",
        "-ms",
        default=None,
        dest="music_set",
        help="Precompiled JSON list of tracks to convert"
    )
    parser.add_argument(
        "--dry-run",
        "-dr",
        default=True,
        dest="dry_run",
        help="Refresh the rrecompiled JSON list of tracks to convert"
    )
    args = parser.parse_args()

    # music_path, excluded, output_path
    music_path = args.music_path
    excluded = args.excluded
    output_path = args.output_path
    music_set_path= args.music_set
    dry_run = args.dry_run

    log.info(f"Music path: {music_path}")
    log.info(f"Output path: {output_path}")
    log.info(f"Excluded directories: {excluded}")
    log.info(f"Music path: {music_path}")
    log.info(f"Dry run: {dry_run}")
    # log.info(f"Excluded directories: {excluded}")

    # Call your function to process music files
    # get_music_structure(music_path, output_path, excluded)
    if music_set_path:
        music_set = load_music_set(music_set_path)
        log.info(f"Music set loaded from {music_set_path}")
    else:
        log.info(f"Creating music set from {music_path}")
        music_set = get_music_set(music_path, excluded)
        save_music_set(music_set, output_path)
    
    if dry_run == "True":
        log.info(f"Dry run: not converting music files")
        log.info(f"Number of music files: {len(music_set)}")
        return

    # Convert the music set to mp3 files
    log.info(f"Converting music set to mp3 files")
    for metadata in music_set:
        write_mp3_file(metadata, output_path)
        
    log.info(f"Completed processing music files in {music_path}")
    

def get_music_set(music_path, excluded=[]):
    log.info(f"Processing root directory: {music_path}")
    music_set = set()
    for dir in os.listdir(music_path):
        count = 0
        if dir in excluded:
            log.info(f"Excluding directory: {dir}")
            continue
        
        # next_set = process_directory(dir_path=os.path.join(music_path, dir), excluded=excluded)
        # music_set = music_set.union(next_set)

        for filename in Path(os.path.join(music_path, dir)).rglob("*.m4a"):
            metadata = get_mp4_metadata(filename)
            if metadata is None:
                continue
            if not music_set.__contains__(metadata):
                count = count + 1
                music_set.add(metadata)

        log.info(f"Loaded directory: {dir}, {count} files")

    log.info(f"Loaded {len(music_set)} unique music files")
    save_music_set(music_set, music_path)
    log.info(f"Music set saved to {music_path}/music_set.json")
    return music_set

def process_directory(dir_path, excluded=[]):
    log.info(f"Processing directory: {dir_path}")
    music_set = set()
    music_files = glob.glob(os.path.join(dir_path, "*.m4a"))
    if not music_files:
        log.info(f"No music files found in directory: {dir_path}")
    else:
        log.info(f"Found {len(music_files)} music files in directory: {dir_path}")
        
        for filename in music_files:
            metadata = get_mp4_metadata(filename)
            music_set.add(metadata)

        log.info(f"Loaded {len(music_set)} unique music files")
        save_music_set(music_set, dir_path)
   
    dirs = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
    for dir in dirs:
        if dir in excluded:
            log.info(f"Excluding directory: {dir}")
            continue

        next_set = process_directory(os.path.join(dir_path, dir), excluded)
        music_set = music_set.union(next_set)

    return music_set

def save_music_set(music_set, output_path):
    # Save the music_set to a JSON file
    music_set_json = [
        {
            "artist": metadata.artist,
            "album": metadata.album,
            "title": metadata.title,
            "track_number": metadata.track_number,
            "genre": metadata.genre,
            "date": metadata.date,
            "filename": str(metadata.filename) 
        }
        for metadata in music_set
    ]
    json_file_path = os.path.join(output_path, "music_set.json")
    with open(json_file_path, "w") as json_file:
        json.dump(music_set_json, json_file, indent=4)
    log.info(f"Music set saved to {json_file_path}")
    
def load_music_set(json_file_path):
    with open(json_file_path, "r") as json_file:
        music_set = json.load(json_file)

    # Convert the loaded JSON data back to Metadata objects
    music_set = [
        Metadata(
            artist=metadata["artist"],
            album=metadata["album"],
            title=metadata["title"],
            track_number=metadata["track_number"],
            genre=metadata["genre"],
            date=metadata["date"],
            filename=metadata["filename"]  # filename is not needed here
        )
        for metadata in music_set
    ]

    return music_set

def write_music_set(music_set, output_path):
    for metadata in music_set:
        write_mp3_file(metadata, output_path)

def get_mp4_metadata(filepath):
    try:    
        mp4file = MP4(filepath)
        artist = mp4file.get("\xa9ART", ["Unknown Artist"])[0]
        title = mp4file.get("\xa9nam", ["Unknown Title"])[0]
        album = mp4file.get("\xa9alb", ["Unknown Album"])[0]
        track_number = mp4file.get("trkn", ["Unknown track Number"])[0][0]
        genre = mp4file.get("\xa9gen", ["Unknown Genre"])[0]
        date = mp4file.get("\xa9day", ["Unknown Date"])[0]
        return Metadata(
            artist=artist,
            album=album,
            title=title, 
            track_number=track_number,
            genre=genre,
            date=date,
            filename=filepath)
        
    except Exception as e:
        log.error(f"Error getting metadata from file {filepath}: {e}")
        return None

def write_mp3_file(metadata, output_path):
    
    output_dir = f"{metadata.artist}-{metadata.album}".replace("/", "_").replace(":", "-")
    output_file = os.path.join(        
        output_path,        
        output_dir, 
        f"{str(metadata.track_number).zfill(2)}-{metadata.title.replace("/", "_").replace(":", "-")}.mp3")
    if os.path.exists(output_file):
        return
    if not os.path.exists(os.path.join(output_path, output_dir)):
        os.makedirs(os.path.join(output_path, output_dir))

    log.info(f"Output file: {output_file}")
    try:
        mp4file = AudioSegment.from_file(metadata.filename, format="m4a")
        mp4file.export(output_file, format="mp3")
    except Exception as e:
        log.error(f"Error exporting file: {e}")
        return
    try:
        tags = EasyID3(output_file)
    except ID3NoHeaderError:
        tags = EasyID3()
        tags.save(output_file)  # Add ID3 header if not present
        tags = EasyID3(output_file)

    try:
        tags["title"] = metadata.title
        tags["artist"] = metadata.artist
        tags["tracknumber"] = str(metadata.track_number)
        tags["album"] = metadata.album
        tags["genre"] = metadata.genre
        tags["date"] = str(metadata.date)
    except KeyError as e:
        log.error(f"KeyError: {e}")
    except ValueError as e:
        log.error(f"KeyError: {e}")
        
    try:
        tags.save()
    except Exception as e:
        log.error(f"Error saving tags: {e}")
        return

if __name__ == "__main__":
    main()
