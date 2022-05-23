

class ChannelItem():
    """ChannelItem class. Used in search."""

    def __init__(self, author="", authorId="", authorUrl="", authorThumbnails=[],
                       subCount=0, videoCount=0, description="", descriptionHtml=""):
        self.author = author
        self.authorId = authorId
        self.authorUrl = authorUrl
        self.authorThumbnails = authorThumbnails
        self.subCount = subCount
        self.videoCount = videoCount
        self.description = description
        self.descriptionHtml = descriptionHtml

    def loadFromDict(self, dct):
        """Loads class info from dictionary"""
        self.author = dct['author']
        self.authorId = dct['authorId']
        self.authorUrl = dct['authorUrl']
        self.authorThumbnails = dct['authorThumbnails']
        self.subCount = dct['subCount']
        self.videoCount = dct['videoCount']
        self.description = dct['description']
        self.descriptionHtml = dct['descriptionHtml']

    def convert(self, cls):
        self.__class__ = cls


