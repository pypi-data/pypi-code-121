from django.conf import settings
from pydantic.error_wrappers import ValidationError

from nwon_django_toolbox.nwon_django_settings import NWONDjangoSettings


def set_settings() -> NWONDjangoSettings:
    """
    Parse Settins from Django settings
    """

    if not hasattr(settings, "NWON_DJANGO"):
        return NWONDjangoSettings()

    if isinstance(settings.NWON_DJANGO, NWONDjangoSettings):
        return settings.NWON_DJANGO

    if not isinstance(settings.NWON_DJANGO, dict):
        raise Exception(
            "The NWON_DJANGO settings need to be of type dict or NWONDjangoSettings"
        )

    try:
        return NWONDjangoSettings.parse_obj(settings.NWON_DJANGO)
    except ValidationError as exception:
        raise Exception(
            f"Could not parse the NWON_DJANGO settings: {str(exception)}"
        ) from exception


NWON_DJANGO_SETTINGS = set_settings()
"""
Settings used withing the NWON-django-toolbox package
"""

__all__ = ["NWON_DJANGO_SETTINGS"]
