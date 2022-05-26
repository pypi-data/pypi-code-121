##
# File: JWTAuthBearer.py
# Date: 23-Aug-2021
#
##
import logging
import os

from fastapi import HTTPException
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from rcsb.app.file.JWTAuthToken import JWTAuthToken

logger = logging.getLogger(__name__)


class JWTAuthBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTAuthBearer, self).__init__(auto_error=auto_error)
        self.__au = JWTAuthToken(os.environ["CACHE_PATH"], os.environ["CONFIG_FILE"])

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTAuthBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Missing Bearer details")
            if not self.validateToken(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid or expired token")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization ")

    def validateToken(self, token: str) -> bool:
        try:
            payload = self.__au.decodeToken(token)
        except Exception:
            payload = None
        return payload is not None
