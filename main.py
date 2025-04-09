# https://irenenaya.medium.com/sorting-your-music-library-with-python-1f0eff8c59cd

import argparse
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
        default=["White Noise", "Audiobooks", "Podcasts", ".DS_Store"],
        dest="excluded",
        # type=str,
        # # type=lambda x: x.split(","),
        help="List of directories to exclude"
    )
    parser.add_argument(
        "--music-set",
        "-ms",
        default=None,
        dest="music_set",
        help="Precompiled JSON list of tracks to convert"
    )
    args = parser.parse_args()

    # music_path, excluded, output_path
    music_path = args.music_path
    excluded = args.excluded
    output_path = args.output_path
    music_set_path= args.music_set

    print(f"Music path: {music_path}")
    print(f"Output path: {output_path}")
    print(f"Excluded directories: {excluded}")
    print(f"Music path: {music_path}")
    # print(f"Excluded directories: {excluded}")

    # Call your function to process music files
    # get_music_structure(music_path, output_path, excluded)
    if music_set_path:
        music_set = load_music_set(music_set_path)
        print(f"Music set loaded from {music_set_path}")
        
    music_set = get_music_set(music_path, output_path, excluded)
    save_music_set(music_set, output_path)
    
    print(f"Converting music set to mp3 files")
    for metadata in music_set:
        write_mp3_file(metadata, output_path)
        
    print(f"Completed processing music files in {music_path}")
    


def get_music_structure(music_path, output_path, excluded=[]):
    print(f"Processing root directory: {music_path}")
    for artist in os.listdir(music_path):
        if artist in excluded:
            print(f"Excluding artist: {artist}")
            continue
        artist_path = os.path.join(music_path, artist)
        if os.path.isdir(artist_path):
            print(f"Processing artist directory: {artist}")
            for album in os.listdir(artist_path):
                if album in excluded:
                    print(f"Excluding album: {album}")
                    continue

                print(f"Processing album: {album}")
                album_path = os.path.join(artist_path, album)
                out_dir = os.path.join(output_path, f"{artist}-{album}")

                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)

                process_album(artist, album, album_path, out_dir)


def process_album(artist, album, input_path, out_dir):
    print(f"Processing album: {album} from artist: {artist}")
    for filepath in Path(input_path).rglob("*.m4a"):
        filename = os.path.basename(filepath)
        metadata = get_mp4_metadata(filepath)

        # track_number = filename[:2]
        # output_file=os.path.join(
        #     out_dir, f"{track_number}-{filename[3:].rstrip(".m4a")}.mp3")
        output_file = os.path.join(
            out_dir, f"{filename[3:].rstrip(".m4a")}.mp3")
        if os.path.exists(output_file):
            print(f"Skipping file: {output_file}")
            continue

        # Load the M4A metadata
        mp4_metadata = MP4(filepath)

        print(f"Creating file: {output_file}")
        # Export as .mp3
        try:
            mp4file = AudioSegment.from_file(filepath, format="m4a")
            mp4file.export(output_file, format="mp3")
        except Exception as e:
            print(f"Error exporting file: {e}")
            continue

        # Add metadata using mutagen
        try:
            tags = EasyID3(output_file)
        except ID3NoHeaderError:
            tags = EasyID3()
            tags.save(output_file)  # Add ID3 header if not present
            tags = EasyID3(output_file)

        tags["title"] = title
        tags["artist"] = artist
        tags["tracknumber"] = str(track_number)
        tags["album"] = album
        tags["genre"] = genre
        tags["date"] = date

        tags.save()

    print(f"Completed album: {album} from artist: {artist}")


def get_music_set(music_path, output_path, excluded=[]):
    print(f"Processing root directory: {music_path}")
    music_set = set()
    for dir in os.listdir(music_path):
        count = 0
        if dir in excluded:
            print(f"Excluding directory: {dir}")
            continue

        print(f"Processing directory: {dir}")

        for filename in Path(os.path.join(music_path, dir)).rglob("*.m4a"):
            metadata = get_mp4_metadata(filename)
            if not music_set.__contains__(metadata):
                music_set.add(metadata)
                count = count + 1

        print(f"Loaded directory: {dir}, {count} files")

    print(f"Loaded {len(music_set)} unique music files")
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
        }
        for metadata in music_set
    ]
    json_file_path = os.path.join(output_path, "music_set.json")
    with open(json_file_path, "w") as json_file:
        json.dump(music_set_json, json_file, indent=4)
    print(f"Music set saved to {json_file_path}")
    
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
            filename=None  # filename is not needed here
        )
        for metadata in music_set
    ]

    return music_set

def write_music_set(music_set, output_path):
    for metadata in music_set:
        write_mp3_file(metadata, output_path)

def get_mp4_metadata(filepath):
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

def write_mp3_file(metadata, output_path):
    output_dir = os.path.join(output_path, f"{metadata.artist}-{metadata.album}")
    output_file = os.path.join(
        output_dir, 
        f"{str(metadata.track_number).zfill(2)}-{metadata.title.replace("/", "-")}.mp3")
    if os.path.exists(output_file):
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Output file: {output_file}")
    try:
        mp4file = AudioSegment.from_file(metadata.filename, format="m4a")
        mp4file.export(output_file, format="mp3")
    except Exception as e:
        print(f"Error exporting file: {e}")
        return
    try:
        tags = EasyID3(output_file)
    except ID3NoHeaderError:
        tags = EasyID3()
        tags.save(output_file)  # Add ID3 header if not present
        tags = EasyID3(output_file)

    tags["title"] = metadata.title
    tags["artist"] = metadata.artist
    tags["tracknumber"] = metadata.track_number
    tags["album"] = metadata.album
    tags["genre"] = metadata.genre
    tags["date"] = metadata.date
    tags.save()

if __name__ == "__main__":
    main()
