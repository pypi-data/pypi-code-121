from random import randint
from typing import Callable, Literal, Any

import phonenumbers as phnbrs
from aioredis import Redis
from loguru import logger
from phonenumbers import PhoneNumberFormat, PhoneNumber, NumberParseException
from pydantic import BaseModel, validator
from jwtserver.settings import Settings
from datetime import datetime, timedelta


class SMSFabric(BaseModel):
    calling: Callable
    send_sms: Callable


class Details(BaseModel):
    block_time: str | None


class ErrorModel(BaseModel):
    text: str
    details: Details | None


class SendDetailsModel(BaseModel):
    method: Literal['call', 'sms']
    block_time: datetime
    attempts: int  # попытки
    ip: str | None

    @validator('block_time', pre=True, always=True)
    def set_block_time_now(cls, v):
        return datetime.fromtimestamp(float(v)) or None


class SendCodeReturnModel(BaseModel):
    is_sent: SendDetailsModel | None = None
    error: ErrorModel | None = None


class SMSRules:
    def __init__(self, settings: Settings, redis):
        self.sms_fabric = settings.sms.sms_fabric(settings.sms)
        self.redis: Redis = redis
        self.ignore_attempts = settings.sms.ignore_attempts
        self.try_call = settings.sms.try_call
        self.time_sms = settings.sms.time_sms
        self.time_calling = settings.sms.time_call
        self.try_sms = settings.sms.try_sms
        self.block_time_minutes = settings.sms.block_time_minutes
        self.general_try_count = self.try_call + self.try_sms

    async def send_code(self, tel: str) -> SendCodeReturnModel:
        """
        Valid phone number check.
        Checking for verification code sending restrictions
        :param tel: Phone number in international format.
        :return: SendCodeReturnModel.
        """
        if not self.tel_is_valid(tel):
            error = ErrorModel(text=f'Wrong number: {tel}.')
            return SendCodeReturnModel(is_sent=None, error=error)

        if await self.limit_is_over(tel):
            error = ErrorModel(text=f'Request limit exceeded: {tel}.')
            return SendCodeReturnModel(is_sent=None, error=error)

        last_code_send = await self.code_is_send(tel)

        if not last_code_send:
            return await self.calling(tel)

        return await self.send_sms(tel)

    async def calling(self, tel) -> SendCodeReturnModel:
        code, error = await self.sms_fabric.calling(tel)
        if error:
            return SendCodeReturnModel(
                is_sent=None,
                error=error)
        block_time = datetime.now() + timedelta(seconds=self.try_call)
        mapping = {
            'method': 'call',
            'block_time': block_time.timestamp(),
            'attempts': 1
        }

        await self.redis.hset(tel, mapping=mapping)
        return SendCodeReturnModel(is_sent=SendDetailsModel(**mapping))

    async def send_sms(self, tel) -> SendCodeReturnModel:
        code = '{:0>4d}'.format(randint(0, 9999))
        sent, error = await self.sms_fabric.send_sms(tel, code)
        if error:
            return SendCodeReturnModel(
                is_sent=None,
                error=error)
        mapping = {'method': 'sms'}
        await self.redis.hset(tel, mapping={'method': 'sms'})
        return SendCodeReturnModel(is_sent=SendDetailsModel(**mapping))

    def tel_is_valid(self, tel) -> bool:
        result_parse = self.parse_tel(tel)
        if result_parse:
            return phnbrs.is_valid_number(self.parse_tel(tel))
        return False

    @staticmethod
    def parse_tel(tel) -> PhoneNumber | None:
        try:
            return phnbrs.parse(tel, None)
        except NumberParseException:
            return None

    async def limit_is_over(self, tel):
        if self.ignore_attempts:
            await self.redis.delete(f'{tel}')
        return self.general_try_count <= await self.get_try_count(tel)

    def code_is_valid(self, code, tel):
        pass

    async def code_is_send(self, tel) -> str | None:
        return await self.redis.hexists(tel, 'method')

    async def get_try_count(self, tel):
        return await self.redis.hget(tel, 'attempts') or 0

    def get_block_time(self, tel):
        pass
    #
    # async def get_ttl_try_count(self, tel):
    #     return await self.redis.ttl(f'{tel}_try_count')
    #
    # async def try_count_incr(self, tel):
    #     return await self.redis.incr(f'{tel}_try_count')
    #
    # async def try_count_decr(self, tel):
    #     return await self.redis.decr(f'{tel}_try_count')
