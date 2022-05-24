#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

"""**DEPRECATED**: Text service"""

import json
import logging
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Text
from datetime import datetime

from skill_sdk import i18n
from skill_sdk.utils.util import CamelModel, validator
from skill_sdk.requests import HTTPError
from skill_sdk.services.base import BaseService

logger = logging.getLogger(__name__)


class Locale(CamelModel):
    """Language code in ISO 639-1 format"""

    code: Text


class LocaleInfo(CamelModel):
    """List of supported languages"""

    supported_languages: List[Locale]

    @validator("supported_languages", each_item=True)
    def check_lang_regex(cls, v: Locale):  # pylint: disable=E0213
        if i18n.RE_TRANSLATIONS.match(v.code):
            return v


class Translation(CamelModel):
    """Text service translation record"""

    # Language
    locale: Text

    # Scope (usually skill name)
    scope: Text

    # Translation tag
    tag: Text

    # Translations (possibly, multiple)
    sentences: List[Text]

    # Tenant, the record is valid for
    tenant: Text

    comment: Optional[Text]
    last_change_date: Optional[datetime]
    creation_date: Optional[datetime]


TranslationCatalog = Dict[Text, Dict[Text, List[Text]]]


class TextService(BaseService):
    """Text (translation) service: stripped version to download full translation catalogue"""

    VERSION = 1
    NAME = "text"

    def __init__(self, url: Text, scope: Text, **kwargs) -> None:
        self.url = url
        self.scope = scope
        super().__init__(url, **kwargs)

    def admin_get_full_catalog(self) -> TranslationCatalog:
        """
        Get a complete translations catalog as {"language": {"key": "value"}} dictionary (admin route only!)

        :return:
        """
        catalog: DefaultDict = defaultdict(dict)

        try:

            logger.debug("Getting locale info...")
            data = self.client.get(f"{self.url}/info/locale").json()
            info = LocaleInfo(**data)
            logger.debug("Locale info: %s", info.dict())

            data = self.client.get(f"{self.url}/scope/{self.scope}").json()
            entries = [Translation(**_) for _ in data]

            [catalog[_.locale].update({_.tag: _.sentences}) for _ in entries]

        except (
            KeyError,
            TypeError,
            HTTPError,
            json.decoder.JSONDecodeError,
        ) as ex:
            logger.error(
                "%s responded with %s. Catalog not available.",
                repr(self.url),
                repr(ex),
            )

        return dict(catalog)
