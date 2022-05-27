import logging
from copy import deepcopy
from dataclasses import dataclass
from time import sleep
from typing import List, Callable, Optional

import requests
from pydash import head

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CorganizeClient:
    host: str
    apikey: str

    @property
    def _default_headers(self):
        return {"apikey": self.apikey}

    def _compose_url(self, resource: str):
        return "/".join([s.strip("/") for s in (self.host, resource)])

    def get_file(self, fileid: str) -> Optional[dict]:
        return head(self.get_files(fileid))

    def get_files(self, *fileids: str) -> List[dict]:
        url = self._compose_url("/files")
        r = requests.get(url, headers=self._default_headers, params={"fileids": "|".join(fileids)})
        r.raise_for_status()
        return r.json().get("files")

    def get_recently_modified_files(self, **kwargs):
        url = self._compose_url("/files")
        return self._get_paginated_files(url, **kwargs)

    def get_least_recently_modified_files(self, **kwargs):
        url = self._compose_url("/files")
        headers = {**self._default_headers, "order": "asc"}
        return self._get_paginated_files(url, headers=headers, **kwargs)

    def get_active_files(self, **kwargs):
        url = self._compose_url("/files/active")
        return self._get_paginated_files(url, **kwargs)

    def get_least_recent_active_files(self, **kwargs):
        url = self._compose_url("/files/active")
        headers = {**self._default_headers, "order": "asc"}
        return self._get_paginated_files(url, headers=headers, **kwargs)

    def get_stale_files(self, **kwargs):
        url = self._compose_url("/files/stale")
        return self._get_paginated_files(url, **kwargs)

    def get_incomplete_files(self, **kwargs):
        url = self._compose_url("/files/incomplete")
        return self._get_paginated_files(url, **kwargs)

    def create_files(self, files: List[dict]):
        assert isinstance(files, list)

        url = self._compose_url("/files/bulk")
        r = requests.post(url, json=files, headers=self._default_headers)

        if not r.ok:
            raise RuntimeError(r.text)

        return r.json()

    def update_file(self, file):
        assert isinstance(file, dict)

        url = self._compose_url("/files")
        r = requests.patch(url, json=file, headers=self._default_headers)

        if not r.ok:
            raise RuntimeError(r.text)

    def delete_files(self, fileids: List[str]):
        assert isinstance(fileids, list)

        url = self._compose_url("/files")
        r = requests.delete(url, json={"fileids": fileids}, headers=self._default_headers)
        r.raise_for_status()

    def get_user_config(self):
        url = self._compose_url("/config")
        r = requests.get(url, headers=self._default_headers)
        r.raise_for_status()
        return r.json()

    def _get_paginated_files(self, url: str, headers: dict = None, limit: int = 1000, interval: int = 0,
                             custom_filter: Callable[[List[dict]], List[dict]] = None):
        return_files = list()

        if not headers:
            LOGGER.debug("headers not provided. Using the default headers...")
            headers = self._default_headers

        headers_deepcopy = deepcopy(headers)

        while True:
            r = requests.get(url, headers=headers_deepcopy)
            r.raise_for_status()

            response_json = r.json()

            files = response_json.get("files")
            metadata = response_json.get("metadata")

            if custom_filter:
                files = custom_filter(files)

            return_files += files

            LOGGER.info(f"{len(files)=} {len(return_files)=}")

            next_token = metadata.get("nexttoken")
            if not next_token or len(return_files) >= limit:
                break

            headers_deepcopy.update({
                "nexttoken": next_token
            })

            LOGGER.info("next_token found")
            sleep(interval)

        LOGGER.info("End of pagination")

        if len(return_files) > limit:
            LOGGER.info(f"Truncating return_files... limit={limit}")
            return return_files[:limit]

        return return_files
