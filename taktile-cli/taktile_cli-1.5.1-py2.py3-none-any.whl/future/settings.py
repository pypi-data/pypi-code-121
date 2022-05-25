"""Module for user exposed env settings"""
import typing as t

from pydantic import BaseSettings


class Settings(BaseSettings):
    TAKTILE_GIT_SHA: str = "unknown"
    TAKTILE_GIT_REF: str = "unknown"
    REPOSITORY_ID: str = "unknown"
    TKTL_MONITORING_ENDPOINT: t.Optional[str] = None


settings = Settings()
