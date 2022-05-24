class BaseCrawlerException(Exception):
    '''base crawler exception
    '''


class CannotFindAction(BaseCrawlerException):
    '''cannot find action
    '''

class CannotParseResponse(BaseCrawlerException):
    '''cannot parsable response
    '''


class FollowNameError(BaseCrawlerException):
    '''follow argument error
    '''

class UrlError(BaseCrawlerException):
    '''UrlError
    '''

class UrlOrderError(BaseCrawlerException):
    '''Url Order Error
    '''


class UrlRendererError(BaseCrawlerException):
    '''url renderer retun value type
    '''

