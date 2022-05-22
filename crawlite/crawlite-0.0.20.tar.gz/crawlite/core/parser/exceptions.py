class BaseParserError(Exception):
    '''Base Parser Error
    '''

class HasNoContentType(BaseParserError):
    '''Response header has no content type info
    '''


class NotParsableContent(BaseParserError):
    '''cannot parse this content type!
    '''



class ExtractorReturnNoneValue(BaseParserError):
    '''
    '''

class CannotExtractError(BaseParserError):
    '''han not beautifulsoup instance
    '''