import os
import secrets

import logging
from typing import Optional

from pydantic import BaseModel, BaseSettings, Field, SecretStr

class Settings(BaseSettings):
    PUBLIC_URL: str = 'http://localhost:8000'
    DEBUG: bool = False
    API_V1_STR: str = '/api/v1'
    BACKEND_CORS_ORIGINS: str = ""
    SECRET: SecretStr = secrets.token_urlsafe()
    DRONE_SERVER: str = Field("", env='drone_server')
    DRONE_TOKEN: str = Field("", env='drone_token')
    DB_DSN: str = 'sqlite://db.sqlite3'
    SMTP_HOST: str = 'smtp.google.com'
    SMTP_PORT: int = 465
    SMTP_USERNAME: Optional[str]
    SMTP_PASSWORD: Optional[str]
    SMTP_FROM_EMAIL: str = 'drone-approval'
    SMTP_REPLY_EMAIL: str = 'drone-approval'

    class Config:
        env_file = os.environ.get('DRONE_APPROVAL_ENVFILE','.env')
        env_prefix = 'DRONE_APPROVAL_'  # defaults to no prefix, i.e. ""

settings = Settings()

logging.info("Settings are %s",settings)

tortoise_orm_models = ['drone_approval.models', "aerich.models"]
tortoise_orm = {
    'connections': {'default':settings.DB_DSN},
    'apps':{
        'models': {
            'models': tortoise_orm_models,
            'default_connection': 'default',
        }
    }
}
