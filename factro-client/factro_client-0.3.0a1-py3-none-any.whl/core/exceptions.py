
class UnauthorizedException(Exception):
    
    MESSAGE = """
        The request failed cause an `401` status code raised.

        Please check the used api_key, maybe it is expired or missing.
    """

    def __init__(self):
        super(UnauthorizedException, self).__init__(UnauthorizedException.MESSAGE)
