#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Skill invoke request"""

import datetime
import logging
from contextlib import ContextDecorator
from contextvars import ContextVar, Token
from typing import Any, Dict, List, Optional, Text
from dateutil import tz

from pydantic import Field

from skill_sdk.__version__ import __spi_version__
from skill_sdk.utils.util import CamelModel, DEFAULT_LOCALE
from skill_sdk.intents import AttributeV2
from skill_sdk.i18n import _, _n, _a, Translations

logger = logging.getLogger(__name__)


class Context(CamelModel):
    """Intent invocation context"""

    # Skill attributes
    attributes: Dict[Text, List[Text]]

    # Skill attributes in extended form
    attributes_v2: Dict[Text, List[AttributeV2]]

    # Skill configuration
    configuration: Dict[Text, Dict]

    # Intent name
    intent: Text

    # Request locale
    locale: Text = Field(example=DEFAULT_LOCALE)

    # Skill id
    skill_id: Optional[Text]

    # Skill tokens
    tokens: Dict[Text, Text]

    # Client type (mini/premium/etc)
    client_type_name: Optional[Text]

    # User profile configuration
    user_profile_config: Optional[Text]

    @staticmethod
    def _(*args, **kwargs):
        return _(*args, **kwargs)

    @staticmethod
    def _n(*args, **kwargs):
        return _n(*args, **kwargs)

    @staticmethod
    def _a(*args, **kwargs):
        return _a(*args, **kwargs)

    def _get_attr_value(self, attr, default=None):
        """Silently return first item from attributes array"""
        try:
            attr_v2 = self.attributes_v2[attr][0]
            return attr_v2.value
        except LookupError:
            logger.error(
                "Attribute %s is not in context. Defaulting to %s",
                repr(attr),
                repr(default),
            )
            return default

    def gettz(self) -> datetime.tzinfo:
        """
        Get device timezone from context attributes

        :return:
        """
        _tz = self._get_attr_value("timezone")
        timezone = tz.gettz(_tz)

        if timezone is None:
            logger.error(
                "Device timezone not present or invalid: %s. Defaulting to UTC",
                repr(_tz),
            )
            timezone = tz.tzutc()

        return timezone

    def today(self) -> datetime.datetime:
        """
        Get `datetime.datetime` object representing the current day at midnight

        :return:
        """
        dt = self.now()
        return datetime.datetime.combine(dt.date(), datetime.time(0))

    def now(self) -> datetime.datetime:
        """Get current device date/time with timezone info

        :return:
        """
        timezone = self.gettz()
        return datetime.datetime.now(datetime.timezone.utc).astimezone(timezone)


class Session(CamelModel):
    """Device session"""

    class Config:
        """Sample values for Swagger UI"""

        schema_extra: Dict = {
            "example": {
                "id": "123",
                "attributes": {"key-1": "value-1", "key-2": "value-2"},
                "new": True,
            }
        }

        # Session is mutable for backward compatibility
        allow_mutation = True

    # Session identifier
    id: Text

    # Session attributes
    attributes: Dict[Text, Text]

    # True if session is new, False for resumed
    new: bool = True

    def __getitem__(self, item):
        return self.attributes.__getitem__(item)

    def __setitem__(self, key, value):
        return self.attributes.__setitem__(key, value)

    def __delitem__(self, key):
        return self.attributes.__delitem__(key)


class InvokeSkillRequest(CamelModel):
    """Skill invocation request"""

    # Invocation context
    context: Context

    # Session
    session: Session

    # Service Provider Interface (SPI) version
    spi_version: Text = Field(example=__spi_version__)

    # Translations to current locale
    _trans: Optional[Translations]

    def get_translation(self) -> Optional[Translations]:
        return self._trans

    def with_translation(self, translation: Translations) -> "InvokeSkillRequest":
        """
        Factory method to add translation to current locale

        :param translation:
        :return:
        """
        return self.copy(update=dict(_trans=translation))


class RequestContextVar(ContextDecorator):
    """Context manager to make InvokeSkillRequest object globally importable"""

    _scope = "request"
    _request_scope_storage: ContextVar[Dict[Text, Any]] = ContextVar(
        "invoke_skill_request"
    )

    __request_token: Optional[Token] = None

    def __init__(self, **kwargs: Any):
        # Deep-copy request to allow mutating session attributes
        self.kwargs = {k: v.copy(deep=True) for k, v in kwargs.items()}

    def __len__(self):
        return 0 if self.__request_token is None else 1

    def __getattr__(self, item):
        try:
            return getattr(self._request_scope_storage.get()[self._scope], item)
        except (AttributeError, LookupError) as e:
            logger.error(
                "Accessing request local object outside of the request-response cycle."
            )
            logger.debug("Details: %s", repr(e))

    def __enter__(self):
        self.__request_token = self._request_scope_storage.set(self.kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._request_scope_storage.reset(self.__request_token)
        if exc_type:
            return False


def _context_var():
    """Wrapper to cheat mypy"""
    return RequestContextVar()


#
# Global objects
#
request: InvokeSkillRequest = _context_var()  # noqa

r = request
