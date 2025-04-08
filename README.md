## Library/utility for managing music collection
I have an extensive collection of music downloaded form iTunes in the days before streaming was a thing. I also have a car. In that car there is a stereo with the ability to read a USB stick. Unfortunately it's kinda dumb, doesn't traverse nested directories, and can't read M4A files. So, I have a need for a utility to: 

- Scan my iTunes collection
- Convert the files to MP3 format so my car can read them 
- Organize the output into a flat folder structure with albums grouped by artist
- Write those files to a USB stick 


### Requirements
FFMpeg (on Mac OS install via `brew install ffmpeg`)

Installed via Pip:
```
    Mutagen
    Pydub
```