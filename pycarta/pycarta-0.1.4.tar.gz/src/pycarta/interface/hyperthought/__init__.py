from .accessors import *
from .base import *
from .parsers import *
from .schema import *
from .setters import *
from hyperthought.auth import Authorization
from typing import Optional


__hyperthoughtAgent = None


def get_hyperthought_auth(token: Optional[str]=None) -> Authorization:
    global __hyperthoughtAgent
    if __hyperthoughtAgent is None:
        if token is None:
            raise ValueError("A HyperThought token must be given to initiate "
                             "a HyperThought Authorization Agent.")
        __hyperthoughtAgent = Authorization(auth_payload=token)
    return __hyperthoughtAgent
