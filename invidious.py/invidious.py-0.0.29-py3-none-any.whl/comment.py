

class Comment:
    """Comment class."""

    def __init__(self, author: str="", authorThumbnails: list=[], authorId: str="",
                authorUrl: str="", isEdited: bool=False, content: str="", 
                contentHtml: str="", published: int=0, publishedText: str="", 
                likeCount: int=0, commentId: str="", authorIsChannelOwner: bool=False,
                verified: bool=False):
        self.author = author
        self.authorThumbnails = authorThumbnails
        self.authorId = authorId
        self.authorUrl = authorUrl
        self.isEdited = isEdited
        self.content = content
        self.contentHtml = contentHtml
        self.published = published
        self.publishedText = publishedText
        self.likeCount = likeCount
        self.commentId = commentId
        self.authorIsChannelOwner = authorIsChannelOwner
        self.verified = verified

    def loadFromDict(self, dct):
        """Loads class info from dictionary"""
        self.author = dct['author']
        self.authorId = dct['authorId']
        self.authorUrl = dct['authorUrl']
        self.authorThumbnails = dct['authorThumbnails']
        self.isEdited = dct['isEdited']
        self.content = dct['content']
        self.contentHtml = dct['contentHtml']
        self.published = dct['published']
        self.publishedText = dct['publishedText']
        self.likeCount = dct['likeCount']
        self.commentId = dct['commentId']
        self.authorIsChannelOwner = dct['authorIsChannelOwner']
        self.verified = dct['verified']

    def convert(self, cls):
        self.__class__ = cls
