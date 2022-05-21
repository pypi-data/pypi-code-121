from typing import Literal
from fastapi import HTTPException
from fastapi.param_functions import Optional, Cookie
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette import status
import hashlib
from loguru import logger
from base64 import b64decode
from json import loads
from datetime import datetime, timedelta

from jwtserver.settings import TokenModel


class Data(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


def secret(string, base_sol: str, temporary_sol: str = ""):
    sol = f"{base_sol[:50]}{temporary_sol}){base_sol[:50]}"
    return hashlib.pbkdf2_hmac(
        'sha256',
        string.encode('ascii'),
        sol.encode('ascii'),
        100000
    ).hex()


class TokenProcessor:
    def __init__(
            self,
            _config: TokenModel,
            refresh_token: str = None,
            access_token: str = None,
    ):
        self.config = _config
        self.access = access_token
        self.new_access = access_token
        self.refresh = refresh_token
        self.new_refresh = refresh_token

    def payload_token_untested(self, token_type: Literal['access', 'refresh']):
        """Token untested payload
        :param str token_type:
        :return dict data: token payload
        """
        return loads(
            b64decode(getattr(self, token_type).split('.', 2)[1] + '=='))

    def payload_token(self, token_type: Literal['access', 'refresh']):
        """Token tested payload
        :param str token_type:
        :return dict data: token payload
        :raises JWTError: If the signature is invalid in any way
        :raises ExpiredSignatureError: If the signature has expired
        :raises JWTClaimsError: If any claim is invalid in any way
        """
        try:
            return jwt.decode(
                getattr(self, token_type), self.config.secret_key,
                algorithms=[self.config.algorithm])
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bad JWT token",
                headers={"WWW-Authenticate": "JSv1"})

    def create_pair_tokens(self, uuid):
        """Create two JWT tokens with a shared secret at the same time
        :return tuple: [access_token, refresh_token]
        """
        access_time = timedelta(minutes=self.config.access_expire_time)
        refresh_time = timedelta(minutes=self.config.refresh_expire_time)

        datetime_now = datetime.now()
        temporary_sol_access = (datetime_now + access_time).timestamp()
        temporary_sol_refresh = (datetime_now + refresh_time).timestamp()
        payload_access = {
            'uuid': uuid,
            'secret': secret(
                uuid,
                base_sol=self.config.base_sol,
                temporary_sol=str(temporary_sol_access))[:32],
            'exp': temporary_sol_access
        }

        payload_refresh = {
            'secret': secret(
                uuid,
                base_sol=self.config.base_sol,
                temporary_sol=str(temporary_sol_refresh))[32:],
            'exp': temporary_sol_refresh,
        }

        access_jwt = jwt.encode(
            payload_access,
            self.config.secret_key,
            algorithm=self.config.algorithm)

        refresh_jwt = jwt.encode(
            payload_refresh,
            self.config.secret_key,
            algorithm=self.config.algorithm)

        logger.info(f'create new {access_jwt=}')
        logger.info(f'create mew {refresh_jwt=}')
        return access_jwt, refresh_jwt
