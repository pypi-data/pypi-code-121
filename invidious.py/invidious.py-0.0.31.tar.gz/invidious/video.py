
class Video():
    """Base Video class. Have maximum options."""

    def __init__(self, title="", videoId="", videoThumbnails=[], storyboards=[], description="", descriptionHtml="",
                       published=0, publishedText="", keywords=[], viewCount=0, likeCount=0, dislikeCount=0,
                       paid=False, premium=False, isFamilyFriendly=False, allowedRegions=[], genre="", genreUrl="",
                       author="", authorId="", authorUrl="", authorThumbnails=[], subCountText="", lengthSeconds=0,
                       allowRatings=False, rating=0, isListed=False, liveNow=False, isUpcoming=False, dashUrl="",
                       adaptiveFormats=[], formatStreams=[], captions=[], recommendedVideos=[]):
        self.title = title
        self.videoId = videoId
        self.videoThumbnails = videoThumbnails
        self.storyboards = storyboards
        self.description = description
        self.descriptionHtml = descriptionHtml
        self.published = published
        self.publishedText = publishedText
        self.keywords = keywords
        self.viewCount = viewCount
        self.likeCount = likeCount
        self.dislikeCount = dislikeCount
        self.paid = paid
        self.premium = premium
        self.isFamilyFriendly = isFamilyFriendly
        self.allowedRegions = allowedRegions
        self.genre = genre
        self.genreUrl = genreUrl
        self.author = author
        self.authorId = authorId
        self.authorUrl = authorUrl
        self.authorThumbnails = authorThumbnails
        self.subCountText = subCountText
        self.lengthSeconds = lengthSeconds
        self.allowRatings = allowRatings
        self.rating = rating
        self.isListed = isListed
        self.liveNow = liveNow
        self.isUpcoming = isUpcoming
        self.dashUrl = dashUrl
        self.adaptiveFormats = adaptiveFormats
        self.formatStreams = formatStreams
        self.captions = captions
        self.recommendedVideos = recommendedVideos

    def loadFromDict(self, dct):
        """Loads ChannelItem info from dictionary"""
        self.title = dct['title']
        self.videoId = dct['videoId']
        self.videoThumbnails = dct['videoThumbnails']
        self.storyboards = dct['storyboards']
        self.description = dct['description']
        self.descriptionHtml = dct['descriptionHtml']
        self.published = dct['published']
        self.publishedText = dct['publishedText']
        self.keywords = dct['keywords']
        self.viewCount = dct['viewCount']
        self.likeCount = dct['likeCount']
        self.dislikeCount = dct['dislikeCount']
        self.paid = dct['paid']
        self.premium = dct['premium']
        self.isFamilyFriendly = dct['isFamilyFriendly']
        self.allowedRegions = dct['allowedRegions']
        self.genre = dct['genre']
        self.genreUrl = dct['genreUrl']
        self.author = dct['author']
        self.authorId = dct['authorId']
        self.authorUrl = dct['authorUrl']
        self.authorThumbnails = dct['authorThumbnails']
        self.subCountText = dct['subCountText']
        self.lengthSeconds = dct['lengthSeconds']
        self.allowRatings = dct['allowRatings']
        self.rating = dct['rating']
        self.isListed = dct['isListed']
        self.liveNow = dct['liveNow']
        self.isUpcoming = dct['isUpcoming']
        self.dashUrl = dct['dashUrl']
        self.adaptiveFormats = dct['adaptiveFormats']
        self.formatStreams = dct['formatStreams']
        self.captions = dct['captions']
        self.recommendedVideos = dct['recommendedVideos']

    def convert(self, cls):
        self.__class__ = cls
