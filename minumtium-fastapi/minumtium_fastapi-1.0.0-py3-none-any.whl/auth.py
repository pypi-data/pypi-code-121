from fastapi import Header, Depends, HTTPException
from minumtium.infra.authentication import AuthenticationService, AuthenticationException

from .deps import auth_service


async def authenticate(x_auth_minumtium: str = Header(None), service: AuthenticationService = Depends(auth_service)):
    if x_auth_minumtium is None:
        raise NoTokenProvidedException()
    try:
        service.validate_token(x_auth_minumtium)
    except AuthenticationException as e:
        raise NotAuthorizedException() from e


class NoTokenProvidedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail='Authentication token has not been provided.')


class NotAuthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail='Not authorized.')
