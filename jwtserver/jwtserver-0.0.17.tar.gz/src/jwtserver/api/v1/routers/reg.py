import datetime
from secrets import token_hex
from aioredis import Redis
from fastapi import Depends, Body, APIRouter, HTTPException, Response
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status
from jwtserver.internal.SMSCRules import SMSRules, SendDetailsModel, \
    SendCodeReturnModel
from jwtserver.settings import Settings, get_settings
from jwtserver.Google.Recaptcha_v3 import Recaptcha
from jwtserver.api.v1.help_func.ParseToken import TokenProcessor
from jwtserver.dependencies.init_redis import redis_conn
from jwtserver.dependencies.session_db import async_db_session
from jwtserver.functions.secure import get_password_hash
from jwtserver.models import User
from pydantic import BaseModel

router = APIRouter(prefix='/api/v1', tags=['Registration'])


class ResponsePhoneStatusModel(BaseModel):
    free: bool
    telephone: str


class CheckCodeResponseModel(BaseModel):
    reg_token: str


class RespError(BaseModel):
    error: str
    block_time: int | None


@router.post('/phone_status', response_model=ResponsePhoneStatusModel,
             name='reg:phone_status')
async def phone_status(
        telephone: str = Body(...),
        recaptcha_token: str = Body(...),
        session: AsyncSession = Depends(async_db_session),
        settings: Settings = Depends(get_settings),
):
    recaptcha = Recaptcha(
        _config=settings.Google.Recaptcha,
        environment=settings.environment,
        recaptcha_token=recaptcha_token,
    )
    await recaptcha.set_action_name('SignUpPage/PhoneStatus').greenlight()
    stmt = select(User).where(User.telephone == telephone)
    result = await session.execute(stmt)
    busy = result.scalars().first()
    return {'free': False if busy else True, 'telephone': telephone}


class RespSendCodeModel(BaseModel):
    send: bool
    block_time: float
    method: str


@router.post('/send_code', response_model=RespSendCodeModel,
             description='Sending a code through a call or SMS',
             name='reg:send_code')
async def send_code(
        telephone: str = Body(...),
        settings: Settings = Depends(get_settings),
        redis: Redis = Depends(redis_conn),
):
    sms_rules = SMSRules(settings, redis)
    result = await sms_rules.send_code(telephone)

    if result.error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": result.error,
                'block_time': result.error.details.block_time
            }
        )

    return {
        "send": True,
        "block_time": result.is_sent.block_time.timestamp(),
        "method": result.is_sent.method,
    }


@router.post('/check_code',
             description="User authorization by login and password",
             # response_description=response_description,
             response_model=CheckCodeResponseModel,

             )
async def check_code(
        # redis: Redis,
        telephone: str = Body(...),
        code: int = Body(...),
        redis: Redis = Depends(redis_conn),
        recaptcha: Recaptcha = Depends(Recaptcha)
):
    """Checking the code from SMS or Call
    :param str telephone: Telephone number in international format
    :param int code: 4 digit verification code
    :param redis: Redis client
    :param recaptcha: Validate Google recaptcha_v3.md v3 [return True or HTTPException]
    :return: one-time token for registration
    """
    await recaptcha.set_action_name('SignUpPage/CheckCode').greenlight()

    code_method = await redis.get(telephone)
    if code_method:
        from_redis_code, method = code_method.split(":")
        if int(from_redis_code) == code:
            reg_token = token_hex(16)
            await redis.set(f"{telephone}_reg_token", reg_token, 60 * 60)
            return {"reg_token": reg_token}

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код",
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Нужно запросить новый код ",
    )


class Data(BaseModel):
    telephone: str
    password: str
    reg_token: str


class AccessTokenResponseModel(BaseModel):
    access_token: str
    token_type: str


@router.post("/signup",
             response_model=AccessTokenResponseModel,
             description="Registration user by login and password",
             status_code=status.HTTP_201_CREATED)
async def reg_user(
        # redis: Redis,
        response: Response,
        data: Data = None,
        # form_data: RegRequestForm = Depends(),
        redis: Redis = Depends(redis_conn),
        session: AsyncSession = Depends(async_db_session)
):
    if not await redis.get(f"{data.telephone}_reg_token"):
        return {"error": "bad reg token"}
    else:
        stmt = select(User).where(User.telephone == data.telephone)
        if (await session.execute(stmt)).scalars().first():
            return {"error": "user exist"}
        else:
            hashed_password = get_password_hash(data.password)
            new_user = User(telephone=data.telephone, is_active=True,
                            password=hashed_password)
            session.add(new_user)
            await session.commit()
            token_processor = TokenProcessor()
            access_token, refresh_token = token_processor.create_pair_tokens(
                new_user.uuid.hex)

            await redis.delete(data.telephone)
            await redis.delete(f"{data.telephone}_reg_token")

            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,
                max_age=settings.token.refresh_expire_time * 60)
            return {"access_token": access_token, "token_type": "JSv1"}


__all__ = ['router']
