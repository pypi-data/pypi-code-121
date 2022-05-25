from pathlib import Path
from typing import Optional, Dict, Any

from pydantic.class_validators import validator
from pydantic.env_settings import BaseSettings
from pydantic.networks import RedisDsn


class RedisSettings(BaseSettings):
    REDIS_TYPE: str = 'redis'
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ''
    REDIS_PASSWORD_FILE: Optional[Path] = None
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 4
    REDIS_POOL_TIMEOUT_SECONDS: int = 5

    REDIS_URL: Optional[RedisDsn] = None

    @validator('REDIS_URL', pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v

        if 'REDIS_PASSWORD_FILE' in values:
            password_file = values.get('REDIS_PASSWORD_FILE')
            if isinstance(password_file, Path) and password_file.exists():
                with password_file.open() as f:
                    values['REDIS_PASSWORD'] = f.read().strip()

        return RedisDsn.build(
            scheme=values.get('REDIS_TYPE'),
            password=values.get('REDIS_PASSWORD'),
            host=values.get('REDIS_HOST'),
            port=str(values.get('REDIS_PORT')),
            path=f'/{values.get("REDIS_DB") or ""}',
        )

    class Config:
        case_sensitive = False
        env_file = '.env'
