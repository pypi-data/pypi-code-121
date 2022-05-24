

class CommentsList:
    """Comments list class."""

    def __init__(self, commentCount: int=0, videoId: str="",
                comments: list=[], continuation: str=""):
        self.commentCount = commentCount
        self.videoId = videoId
        self.comments = comments
        self.continuation = continuation

    def loadFromDict(self, dct):
        """Loads class info from dictionary"""
        self.commentCount = dct['commentCount']
        self.videoId = dct['videoId']
        self.comments = dct['comments']
        self.continuation = dct['continuation']

    def convert(self, cls):
        self.__class__ = cls
