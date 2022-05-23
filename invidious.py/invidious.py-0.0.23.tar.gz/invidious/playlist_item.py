

class PlaylistItem():
    """PlaylistItem class. Used in search."""

    def __init__(self, title="", playlistId="", author="",
                       authorId="", authorUrl="", videoCount=0, videos=[]):
        """PlaylistItem class. Used in search."""
        self.title = title
        self.playlistId = playlistId
        self.author = author
        self.authorId = authorId
        self.authorUrl = authorUrl
        self.videoCount = videoCount
        self.videos = videos

    def loadFromDict(self, dct):
        """Loads class info from dictionary"""
        self.title = dct['title']
        self.playlistId = dct['playlistId']
        self.author = dct['author']
        self.authorId = dct['authorId']
        self.authorUrl = dct['authorUrl']
        self.videoCount = dct['videoCount']
        self.videos = dct['videos']

    def convert(self, cls):
        self.__class__ = cls


