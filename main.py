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

from music import Music
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
    args = parser.parse_args()

    # music_path, excluded, output_path
    music_path = args.music_path
    excluded = args.excluded
    output_path = args.output_path

    print(f"Music path: {music_path}")
    print(f"Output path: {output_path}")
    # print(f"Excluded directories: {excluded}")

    # Call your function to process music files
    get_music_structure(music_path, output_path, excluded)


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
        track_number = filename[:2]
        output_file=os.path.join(
            out_dir, f"{track_number}-{filename[3:].rstrip(".m4a")}.mp3")
        if os.path.exists(output_file):
            print(f"Skipping file: {output_file}")
            continue
        
        print(f"Creating file: {output_file}")
        # Load the M4A metadata
        mp4_metadata = MP4(filepath)

        # print(f"Processing file: {mp4file.filename}")
        artist = mp4_metadata.get("\xa9ART", ["Unknown Artist"])[0]
        title = mp4_metadata.get("\xa9nam", ["Unknown Title"])[0]
        album = mp4_metadata.get("\xa9alb", ["Unknown Album"])[0]
        track_number = mp4_metadata.get("trkn", ["Unknown track Number"])[0][0]
        genre = mp4_metadata.get("\xa9gen", ["Unknown Genre"])[0]
        date = mp4_metadata.get("\xa9day", ["Unknown Date"])[0]
        # disk_number = mp4_metadata.get("disk", ["Unknown Disk Number"])[0][0]
        # comment = mp4_metadata.get("\xa9cmt", ["Unknown Comment"])[0]
        #music = Music(artist, album, title, track_number)
        #music_set.add(music)        
        
        # Create the output file path
        #print(f"Output file: {output_file}")
        # Load the .m4a file
        mp4file=AudioSegment.from_file(filepath, format="m4a")

        # Export as .mp3
        mp4file.export(output_file, format="mp3")
        
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

def get_music(music_path, output_path, excluded=[]):
    print(f"Processing root directory: {music_path}")
    music_set = set()
    for root, dirs, files in os.walk(music_path):
        
        for dir in dirs:
            if dir in excluded:
                print(f"Excluding directory: {dir}")
                continue
            
            print(f"Processing directory: {dir}")
                    
            for filename in Path(dir).rglob("*.m4a"):
                #print(filename)

                # Load the M4A file
                mp4file = MP4(filename)

                # print(f"Processing file: {mp4file.filename}")
                artist = mp4file.get("\xa9ART", ["Unknown Artist"])[0]
                title = mp4file.get("\xa9nam", ["Unknown Title"])[0]
                album = mp4file.get("\xa9alb", ["Unknown Album"])[0]
                track_number = mp4file.get("trkn", ["Unknown track Number"])[0][0]
                genre = mp4file.get("\xa9gen", ["Unknown Genre"])[0]
                date = mp4file.get("\xa9day", ["Unknown Date"])[0]
                disk_number = mp4file.get("disk", ["Unknown Disk Number"])[0][0]
                comment = mp4file.get("\xa9cmt", ["Unknown Comment"])[0]
                music = Music(artist, album, title, track_number)
                music_set.add(music)
                
                out_dir = os.path.join(output_path, f"{artist}-{album}")
                output_file=os.path.join(
                    out_dir, f"{str(track_number).zfill(2)}-{os.path.basename(filename).rstrip(".m4a")}.mp3")
                if os.path.exists(output_file):
                    #print(f"File already exists: {output_file}")
                    continue
                
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)

                # Create the output file path
                print(f"Output file: {output_file}")
                # Load the .m4a file
                mp4file=AudioSegment.from_file(filename, format="m4a")

                # Export as .mp3
                mp4file.export(output_file, format="mp3")
                
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
                tags["comment"] = comment
                tags["disk"] = str(disk_number)

                tags.save()

            print(f"Completed directory: {dir}")
        # # Access ID3 tags (metadata)
        # for tag in audio.tags:
        #     print(f"{tag}: {audio.tags[tag]}")


        # # remove unwanted directories from the list
        # for i in range(len(dirs)-1, -1, -1):
        #     if dirs[i] in excluded:  # excluded is the list of unwanted directories
        #         del dirs[i]
        #         continue

        # for f in files:
        #     found = False  # bool to store whether we found the metadata
        #     paths = root.split("//")
        #     curr = paths[len(paths)-1]
        #     # search mp3. If metadata returns a recording year, we set bool to True and there’s no need to check other files
        #     if f.endswith(".mp3"):
        #         try:
        #             file_data = metadata.list(root + "/" + f)
        #         except:
        #             # here you can do what you want. I wrote to a separate file for debugging. If data retrieving failed, try next file
        #             continue
        #     count = 0  # counter to make sure we get all 3 elements
        #     if "recording_year" in file_data:
        #         date = str(file_data["recording_year"])
        #         count += 1
        #     if "authors" in file_data:
        #         artist = str(file_data["authors"][0])
        #         count += 1
        #     if "album" in file_data:
        #         album = file_data["album"]
        #         count += 1
        #     if count == 3:
        #         found = True
        #         musicSet.add(Music(date, artist, album))
        #         break  # if we're here, we have our data, no need to continue iterating files in this directory

        # if not found:  # this was the bool we set up at the beginning of the loop. If we're here, neither library above worked as expected.
        #     album = preparePath(root)
        #     # first search by name. Get id from result, then search the release by id to get the year
        # try:
        #     results = discog.search(album, type="release")
        #     # if there’s no results, count will be 0
        #     if results.count < 1:
        #         break
        #     id = results[0].id
        #     release = discog.release(id)
        #     musicSet.add(
        #         Music(str(release.year), release.artists[0].name, release.title))
        # except:
        #     continue
        # break


if __name__ == "__main__":
    main()
