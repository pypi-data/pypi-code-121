"""
HTTP verb module
"""
import enum


# Supported Http Verbs
class HttpVerb(enum.Enum):
    """
    Supported HTTP verbs
    """

    GET = 'GET'
    POST = 'POST'
