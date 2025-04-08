# https://irenenaya.medium.com/sorting-your-music-library-with-python-1f0eff8c59cd

import argparse
import os
# load the libraries that we'll use
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import mutagen.id3
from mutagen.id3 import ID3, TIT2, TIT3, TALB, TPE1, TRCK, TYER

import glob

#import numpy as np

from music import Music
#smb://melnas._smb._tcp.local/melnas/iTunes/Music
#/dev/disk4

def main():
    parser = argparse.ArgumentParser(description="Music Library Organizer")
    parser.add_argument(
        "--music-path",
        "-mp",
        dest="music_path",
        required=True,
        help="Path to traverse for music files"
    )
    parser.add_argument(
        "--output-path",
        "-op",
        dest="output_path",
        required=True,
        help="Path to the output directory"
    )
    parser.add_argument(
        "--excluded",
        nargs="+",
        default=[],
        help="List of directories to exclude"
    )
    args = parser.parse_args()

    #music_path, excluded, output_path
    music_path = args.music_path
    excluded = args.excluded
    output_path = args.output_path

    print(f"Music path: {music_path}")
    print(f"Output path: {output_path}")
    print(f"Excluded directories: {excluded}")

    # Call your function to process music files
    get_music(music_path)

def get_music(music_path):
    global musicSet
    musicSet = set()
    for root, dirs, files in os.walk(music_path):
        print(f"Processing directory: {root}")
        print(f"Files: {files}")
        print(f"Directories: {dirs}")
        
        break
    
    
        # remove unwanted directories from the list
        for i in range(len(dirs)-1, -1, -1):
            if dirs[i] in excluded:  # excluded is the list of unwanted directories
                del dirs[i]
                continue

        for f in files:
            found = False  # bool to store whether we found the metadata
            paths = root.split("//")
            curr = paths[len(paths)-1]
            # search mp3. If metadata returns a recording year, we set bool to True and there’s no need to check other files
            if f.endswith(".mp3"):
                try:
                    file_data = metadata.list(root + "/" + f)
                except:
                    # here you can do what you want. I wrote to a separate file for debugging. If data retrieving failed, try next file
                    continue
            count = 0  # counter to make sure we get all 3 elements
            if "recording_year" in file_data:
                date = str(file_data["recording_year"])
                count += 1
            if "authors" in file_data:
                artist = str(file_data["authors"][0])
                count += 1
            if "album" in file_data:
                album = file_data["album"]
                count += 1
            if count == 3:
                found = True
                musicSet.add(Music(date, artist, album))
                break  # if we're here, we have our data, no need to continue iterating files in this directory

        if not found:  # this was the bool we set up at the beginning of the loop. If we're here, neither library above worked as expected.
            album = preparePath(root)
            # first search by name. Get id from result, then search the release by id to get the year
        try:
            results = discog.search(album, type="release")
            # if there’s no results, count will be 0
            if results.count < 1:
                break
            id = results[0].id
            release = discog.release(id)
            musicSet.add(
                Music(str(release.year), release.artists[0].name, release.title))
        except:
            continue
        break


if __name__ == "__main__":
    main()
