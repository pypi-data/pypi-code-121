from datetime import timedelta, tzinfo
from typing import Any, Dict, Union

import pytz
from pydantic import BaseSettings, validator
from pytimeparse.timeparse import timeparse


class Settings(BaseSettings):
    TIMEZONE: tzinfo = pytz.UTC
    DEBUG: bool = False

    DATABASE_ECHO: bool = True
    DATABASE_POOL_MIN_SIZE: int = 1
    DATABASE_POOL_MAX_SIZE: int = 8
    DATABASE_POOL_EXPIRE_SECONDS: int = 60
    DATABASE_POOL_TIMEOUT_SECONDS: int = 15

    DEFAULT_CACHE_TTL: timedelta = timedelta(seconds=timeparse('1 min'))

    @validator('TIMEZONE', pre=True)
    def set_timezone(cls, v: Union[str, tzinfo], values: Dict[str, Any]) -> tzinfo:
        if isinstance(v, tzinfo):
            return v
        return pytz.timezone(v)

    @validator('DATABASE_ECHO', pre=True)
    def set_db_echo(cls, v: bool, values: Dict[str, Any]) -> bool:
        return values['DEBUG']

    @validator('DEFAULT_CACHE_TTL', pre=True)
    def set_default_ttl(cls, v: Union[str, timedelta], values: Dict[str, Any]) -> timedelta:
        if isinstance(v, timedelta):
            return v
        return timedelta(seconds=timeparse(v))

    class Config:
        case_sensitive = False
        env_file = '.env'
