from loguru import logger
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from starlette import status

from jwtserver import crud
from jwtserver.api.v1.help_func.ParseToken import TokenProcessor
from jwtserver.Google.Recaptcha_v3 import Recaptcha
from jwtserver.app import app
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Response, HTTPException, Body
from jwtserver.functions.secure import verify_password
from jwtserver.functions.session_db import async_db_session
from jwtserver.models import User
from jwtserver.functions.config import load_config

token_config = load_config().token

response_description = """
There will also be response set_cookie refresh_token.
"""


class LoginResponseModel(BaseModel):
    access_token: str
    token_type: str


@app.post("/api/v1/login/",
          response_model=LoginResponseModel,
          tags=["Authorization"],
          description="User authorization by login and password",
          response_description=response_description,
          )
async def login(
        response: Response,
        recaptcha: Recaptcha = Depends(Recaptcha),
        telephone: str = Body(...),
        password: str = Body(...)
):
    """
    More here https://jwtserver.darkdeal.net/en/api_v1/#login
    :param response: Fastapi response
    :param recaptcha: https://jwtserver.darkdeal.net/en/recaptcha_v3/
    :param telephone: international phone number format
    :param password: string
    :raises HTTPException: recaptcha_v3 raises
    :raises HTTPException: If there is no user
    :return LoginResponse
    """
    await recaptcha.set_action_name('LoginPage/LoginButton').greenlight()
    user = await crud.get_user(telephone)
    logger.debug(telephone, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный номер или пароль",
            headers={"WWW-Authenticate": "JSv1"},
        )

    if verify_password(password, user.password):
        token_processor = TokenProcessor()
        logger.debug(token_processor)
        access_token, refresh_token = token_processor.create_pair_tokens(user.uuid.hex)
        logger.debug(access_token, refresh_token)
        logger.debug(access_token, refresh_token)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,
            max_age=token_config.refresh_expire_time * 60)

        logger.debug({"access_token": access_token, "token_type": "JSv1"})
        return {"access_token": access_token, "token_type": "JSv1"}

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный номер или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
