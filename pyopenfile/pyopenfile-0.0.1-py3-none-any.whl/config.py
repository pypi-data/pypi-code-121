import os
from logging.config import dictConfig

from pydantic import BaseSettings, validator, Field

from app.exceptions import ConfigErr, PathErr


class Settings(BaseSettings):
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    logger_level: str = Field(default="DEBUG")
    logger_root_path: str = Field(default="/var/log/openfile")
    data_path: str = Field(default="/var/run/openfile-data")

    @validator("data_path")
    def check_data_path(cls, v, values):
        if not os.path.isabs(v):
            raise ConfigErr("'data_path' should be abs path")

        if not os.path.exists(v):
            raise PathErr("path '{v}' not exists")

        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def _gen_log_path(file):
    return os.path.join(settings.logger_root_path, file)


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s %(module)s : %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "app": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": _gen_log_path("app.log"),
                "backupCount": 3,
                "formatter": "default",
            },
        },
        "loggers": {
            "app": {
                "handlers": ["app", "console"],
                "level": settings.logger_level,
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": settings.logger_level,
        },
    }
)
