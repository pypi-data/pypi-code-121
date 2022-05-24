#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Skill info response"""

from typing import Text, Tuple

from skill_sdk.utils.util import CamelModel
from skill_sdk.__version__ import __spi_version__


class SkillInfoResponse(CamelModel):
    """Skill information response DTO. Expected at `GET <skill-URL>/info` endpoint

    Example:
    {
      "version": "v1",
      "skillSpiVersion": "0.7",
      "skillVersion": "skill-version",
      "id": "id",
      "skillId": "skillId",
      "supportedLocales": [
        "de",
        "en",
        "fr"
      ]
    }

    """

    # Skill ID
    skill_id: Text

    # Skill version
    skill_version: Text

    # Supported locales
    supported_locales: Tuple[Text, ...] = ("de",)

    # Supported SPI version
    skill_spi_version: Text = __spi_version__
