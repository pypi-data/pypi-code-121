import logging
import webbrowser

from pyrasgo.api.error import APIError
from pyrasgo.config import set_session_api_key
from pyrasgo.version import __version__

__all__ = [
    '__version__',
    'connect',
    'open_docs',
    'pronounce_rasgo',
    'login',
]


def connect(api_key):
    from pyrasgo.rasgo import Rasgo

    set_session_api_key(api_key)
    return Rasgo()


def open_docs():
    webbrowser.open("https://docs.rasgoml.com/rasgo-docs/reference/pyrasgo")


def pronounce_rasgo():
    webbrowser.open("https://www.spanishdict.com/pronunciation/rasgo?langFrom=es")


def login(email: str, password: str):
    from pyrasgo.api.login import Login
    from pyrasgo.schemas.user import UserLogin

    payload = UserLogin(
        email=email,
        password=password,
    )
    try:
        response = Login().login(payload=payload)
        return connect(api_key=response)
    except APIError:
        logging.error("Unable to log user in with credentials provided")
