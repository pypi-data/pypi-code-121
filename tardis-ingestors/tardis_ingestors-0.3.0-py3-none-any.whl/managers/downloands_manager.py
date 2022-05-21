import os
import random
import secrets
import time
import urllib.error
from datetime import date, timedelta
from pathlib import Path
from typing import Callable, List

import dateutil.parser
import requests
from tardis.utils import file_name_nested


class DownloadsManager:
    def __init__(
        self,
        download_url_base="datasets.tardis.dev",
        max_attempts: int = 5,
    ):
        self.download_url_base = download_url_base
        self.max_attempts = max_attempts
        self.url = (
            "https://{base}/v1/{exchange}/{data_type}/{date}/{symbol}.{format}.gz"
        )

    def _download_file(self, url: str, download_path: Path, headers: dict):
        response = requests.get(url, stream=True, headers=headers)

        if response.status_code != 200:
            error_text = response.text
            raise urllib.error.HTTPError(
                url, code=response.status_code, msg=error_text, hdrs=None, fp=None
            )
        # ensure that directory where we want to download data exists
        Path(download_path).parent.mkdir(parents=True, exist_ok=True)
        temp_download_path = Path(f"{download_path}{secrets.token_hex(8)}.unconfirmed")

        try:
            # write response stream to unconfirmed temp file
            with temp_download_path.open("wb") as temp_file:
                for data in response.iter_content():
                    temp_file.write(data)

            # rename temp file to desired name only if file has been fully and successfully saved
            # it there is an error during renaming file it means that target file aready exists
            # and we're fine as only successfully save files exist
            try:
                os.replace(temp_download_path, download_path)
            except Exception as ex:
                pass
        finally:
            # cleanup temp files if still exists
            if os.path.exists(temp_download_path):
                os.remove(temp_download_path)

    def _reliably_download_file(self, url: str, download_path: Path, headers: dict):
        attempts = 0

        if os.path.exists(download_path):
            return

        while True:
            attempts = attempts + 1

            try:
                self._download_file(url, download_path, headers)
                break

            except Exception as ex:
                too_many_requests = False

                if attempts == self.max_attempts or isinstance(ex, RuntimeError):
                    raise ex

                if isinstance(ex, urllib.error.HTTPError):
                    # do not retry when we've got bad or unauthorized request or enough attempts
                    if ex.code == 400 or ex.code == 401:
                        raise ex
                    if ex.code == 429:
                        too_many_requests = True

                attempts_delay = 2**attempts
                next_attempts_delay = random.random() + attempts_delay

                if too_many_requests:
                    # when too many requests error received wait longer than normal
                    next_attempts_delay += 3 * attempts

                time.sleep(next_attempts_delay)

    def download(
        self,
        exchange: str,
        data_types: List[str],
        symbols: List[str],
        from_date: str,
        to_date: str,
        format: str = "csv",
        download_dir="./datasets",
        api_key: str = "",
        get_filename: Callable[[str, str, str, date, str], str] = file_name_nested,
    ):
        headers = {"Authorization": f"Bearer {api_key}" if api_key else ""}
        end_date = dateutil.parser.isoparse(to_date)
        for symbol in symbols:
            symbol = symbol.replace(":", "-").replace("/", "-").upper()
            for data_type in data_types:
                current_date = dateutil.parser.isoparse(from_date)
                while True:
                    url = self.url.format(
                        base=self.download_url_base,
                        exchange=exchange,
                        data_type=data_type,
                        date=current_date.strftime("%Y/%m/%d"),
                        symbol=symbol,
                        format=format,
                    )
                    filename = get_filename(
                        exchange, data_type, current_date, symbol, format
                    )
                    filepath = Path(download_dir) / filename

                    self._reliably_download_file(url, filepath, headers)

                    current_date = current_date + timedelta(days=1)
                    if current_date >= end_date:
                        break
