



class ShortVideo():
    """ShortVideo class. Used in popular videos."""

    def __init__(self, title="", videoId=0, videoThumbnails=[], author="",
                 auhtorId="", auhtorUrl="", lengthSeconds=0, 
                 viewCount=0, published=0, publishedText=""):
        self.title = title
        self.videoId = videoId
        self.videoThumbnails = videoThumbnails
        self.author = author
        self.authorId = auhtorId
        self.authorUrl = auhtorUrl
        self.lengthSeconds = lengthSeconds
        self.viewCount = viewCount
        self.published = published
        self.publishedText = publishedText

    def loadFromDict(self, dct):     
        """Loads class info from dictionary"""   
        self.title = dct['title']
        self.videoId = dct['videoId']
        self.videoThumbnails = dct['videoThumbnails']
        self.author = dct['author']
        self.authorId = dct['authorId']
        self.authorUrl = dct['authorUrl']
        self.lengthSeconds = dct['lengthSeconds']
        self.viewCount = dct['viewCount']
        self.published = dct['published']
        self.publishedText = dct['publishedText']

    def convert(self, cls):
        self.__class__ = cls


