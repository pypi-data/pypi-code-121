import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    BASE_DIR: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    # TODO: pasar estas credenciales con secrets de AWS
    BIGQUERY_CREDENTIALS_FILE: str
    BIGQUERY_PROJECT_ID: str
    PATH_BIGQUERY_MODELS: str = "bq_creator/core/models/{}.json"
    BIGQUERY_MODELS: list = [
        "twitter",
        "facebook",
        "google",
        "instagram",
        "tiktok",
        "youtube",
        "summary",
    ]


settings = Settings()
