

class RecommendedVideo():
    """RecommendedVideo class. Used in recommendedVideos option of Video class."""

    def __init__(self, title="", videoId=0, videoThumbnails=[], author="",
                 authorId="", authorUrl="", lengthSeconds=0, 
                 viewCount=0, viewCountText=""):
        self.title = title
        self.videoId = videoId
        self.videoThumbnails = videoThumbnails
        self.author = author
        self.authorId = authorId
        self.authorUrl = authorUrl
        self.lengthSeconds = lengthSeconds
        self.viewCount = viewCount
        self.viewCountText = viewCountText

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
        self.viewCountText = dct['viewCountText']

    def convert(self, cls):
        self.__class__ = cls
