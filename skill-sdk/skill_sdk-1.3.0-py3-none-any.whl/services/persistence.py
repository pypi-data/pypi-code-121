#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

"""Persistence service"""

import json
import logging
from typing import Any, Dict, Text

from skill_sdk.requests import HTTPError, Response
from skill_sdk.services.base import BaseService

PARSE_EXCEPTION = "%s responded with error. Data not available: %s"
REQUEST_EXCEPTION = "%s did not respond: %s"

logger = logging.getLogger(__name__)


class PersistenceService(BaseService):
    """Persistence service: a simple key-value store"""

    VERSION = 1
    NAME = "persistence"

    async def _get(self, path: str) -> Dict[Text, Any]:
        """
        Read the data from service

        :param path:
        :return:
        """

        try:
            async with self.async_client as client:
                _url = "/".join((self.url, path.strip("/\\")))

                data = await client.get(_url)
                return data.json()
        except (
            HTTPError,
            json.decoder.JSONDecodeError,
        ) as ex:
            logger.error(
                "%s responded with %s. Data not available.",
                repr(self.url),
                repr(ex),
            )
            raise

    async def get(self) -> Dict[Text, Any]:
        """
        Read the skill data

        :return:
        """
        return await self._get("entry/data")

    async def get_all(self) -> Dict[Text, Any]:
        """
        Read all the data

        :return:
        """
        return await self._get("entry")

    async def set(self, data: Dict[str, Any]) -> Response:
        """
        Update/Insert the data

        :param data:    data
        :return:
        """
        try:

            async with self.async_client as client:
                _url = f"{self.url}/entry"
                return await client.post(_url, json=dict(data=data))

        except HTTPError as ex:
            logger.error(
                "%s responded with %s. Data not changed.",
                repr(self.url),
                repr(ex),
            )
            raise

    async def delete(self) -> Response:
        """
        Delete all data

        :return:
        """
        try:

            async with self.async_client as client:
                _url = f"{self.url}/entry"
                return await client.delete(_url)

        except HTTPError as ex:
            logger.error(
                "%s responded with %s. Data not deleted.",
                repr(self.url),
                repr(ex),
            )
            raise
