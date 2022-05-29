from typing import List, Optional

import humps
from pydantic import BaseModel, Field


class NWONDjangoSettings(BaseModel):
    """
    Settings for the NWON-django-toolbox package.

    These can be set in the Django configuration by using the key NWON_DJANGO and
    providing a dictionary that resembles this schema.
    """

    authorization_prefix: str = Field(
        default="Bearer",
        description="Authorization prefix for API calls",
    )

    logger_name: str = Field(
        default="nwon-django",
        description="Logger that is used in the whole package",
    )

    file_encoding: str = Field(
        default="utf-8",
        description="Default File encoding used for all file operations",
    )

    keys_to_skip_on_api_test: List[str] = Field(
        default=[],
        description="On some API test helper we check the returned objects against the initial parameters. During this check the given keys are skipped",
    )

    application_name: Optional[str] = Field(
        default=None,
        description="Application name that is used whenever needed",
    )

    api_docs_url: Optional[str] = Field(
        default=None,
        description="Url to the API docs. Used for error handler",
    )

    # Basically the same config as PydanticBaseDjango but we can't import because of a circular import problem
    class Config:
        # no additional properties
        extra = "forbid"

        # Allow initialization via attribute names and aliases
        allow_population_by_field_name = True

        # auto generate camelized aliases
        alias_generator = humps.camelize


__all__ = ["NWONDjangoSettings"]
