class Music:
 def __init__(self, date, artist, album):
   self.date = date
   self.artist = artist
   self.album = album
 def __eq__(self, other):
   return ((self.date == other.date) and (self.artist ==   other.artist) and (self.album == other.album))
 def __hash__(self):
   return hash((self.date, self.artist, self.album))
