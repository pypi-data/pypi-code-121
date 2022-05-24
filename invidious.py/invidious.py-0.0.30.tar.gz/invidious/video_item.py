

class VideoItem():
    """VideoItem class. Used in search."""

    def __init__(self, title="", videoId="", author="", authorId="", authorUrl="",
                       videoThumbnails=[], description="", descriptionHtml="",
                       viewCount=0, published=0, publishedText="", lengthSeconds=0, 
                       liveNow=False, premium=False, isUpcoming=False):
        """VideoItem class. Used in search."""
        self.title = title
        self.videoId = videoId
        self.author = author
        self.authorId = authorId
        self.authorUrl = authorUrl
        self.videoThumbnails = videoThumbnails
        self.description = description
        self.descriptionHtml = descriptionHtml
        self.viewCount = viewCount
        self.published = published
        self.publishedText = publishedText
        self.lengthSeconds = lengthSeconds
        self.liveNow = liveNow
        self.premium = premium
        self.isUpcoming = isUpcoming

    def loadFromDict(self, dct):
        """Loads class info from dictionary"""
        self.title = dct['title']
        self.videoId = dct['videoId']
        self.author = dct['author']
        self.authorId = dct['authorId']
        self.authorUrl = dct['authorUrl']
        self.videoThumbnails = dct['videoThumbnails']
        self.description = dct['description']
        self.descriptionHtml = dct['descriptionHtml']
        self.viewCount = dct['viewCount']
        self.published = dct['published']
        self.publishedText = dct['publishedText']
        self.lengthSeconds = dct['lengthSeconds']
        self.liveNow = dct['liveNow']
        self.premium = dct['premium']
        self.isUpcoming = dct['isUpcoming']

    def convert(self, cls):
        self.__class__ = cls


