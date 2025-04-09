class Metadata:
    def __init__(self, artist, album, title, track_number, genre, date, filename):
        self.artist = artist
        self.album = album
        self.title = title
        self.track_number = track_number
        self.genre = genre
        self.date = date
        self.filename = filename

    def __eq__(self, other):
        return ((self.title == other.title) and
                (self.artist == other.artist) and
                (self.album == other.album) and
                (self.track_number == other.track_number))

    def __hash__(self):
        return hash((self.artist, self.album, self.title, self.track_number))
