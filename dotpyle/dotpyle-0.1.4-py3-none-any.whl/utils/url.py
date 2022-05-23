from enum import Enum


class Protocol(Enum):
    """
    Enum for the different protocols.
    """

    HTTPS = "https"
    SSH = "ssh"


def get_default_url(url: str, protocol: Protocol, token: str = None):
    """
    Return the default URL to clone the content.
    """

    default_url = url

    if protocol == "https" and token is not None:
        default_url = "{0}{1}@{2}".format(url[:8], token, url[9:])

    return default_url
