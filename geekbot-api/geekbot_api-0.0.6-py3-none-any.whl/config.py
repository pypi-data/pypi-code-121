import os

from pydantic import AnyUrl
from pydantic import BaseSettings


class GeekbotAPIConfig(BaseSettings):
    api_key: str
    base_api_path: AnyUrl = "https://api.geekbot.com"  # type: ignore
    api_version: str = "v1"

    class Config:
        env_prefix = os.environ.get("GEEKBOT_API_ENV_PREFIX", "GEEKBOT")
