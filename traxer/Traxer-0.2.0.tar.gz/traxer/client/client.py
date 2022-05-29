
from .session import Session

def connect(url):
    """Connect to a xpipe server

    Args:
        url (str): URL of the server hosting the xpipe API

    Returns:
        session (Session): A session
    """
    return Session(url)
