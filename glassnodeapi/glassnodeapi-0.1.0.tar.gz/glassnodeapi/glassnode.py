import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Union

import iso8601
import pandas as pd
import requests
from requests.utils import default_headers

from .enums import Format
from .enums import FrequencyInterval
from .enums import TimestampFormat

ENDPOINT = "https://api.glassnode.com"


@dataclass
class Parameters:
    asset: str
    since: datetime = None
    until: datetime = None
    frequency_interval: FrequencyInterval = None
    format: Format = None
    timestamp_format: TimestampFormat = None

    def to_dict(self) -> dict:
        params = {'a': self.asset}

        if self.since is not None:
            params['s'] = int(self.since.timestamp())

        if self.until is not None:
            params['u'] = int(self.until.timestamp())

        if self.frequency_interval is not None:
            params['i'] = self.frequency_interval.value

        if self.format is not None:
            params['f'] = self.format.value

        if self.timestamp_format is not None:
            params['timestamp_format'] = self.timestamp_format.value

        return params


class Glassnode(object):

    def __init__(self, api_key: str) -> None:
        self.headers = default_headers()

        # attach API key
        self.headers['X-Api-Key'] = api_key

    def build_url(self, category: str, metric: str):
        return os.path.join(ENDPOINT, 'v1', 'metrics', category, metric)

    def _get(self, category: str, metric: str, params: Parameters) -> pd.Series:
        url = self.build_url(category, metric)

        res = requests.get(url, params=params.to_dict(), headers=self.headers)
        res.raise_for_status()

        df = pd.DataFrame(json.loads(res.text))
        df = df.set_index('t')
        df.index = pd.to_datetime(df.index, unit='s')
        df = df.sort_index()

        s = df['v']
        s.name = f'{category}_{metric}'

        return s

    def get(self,
            category: str,
            metric: str,
            asset: str,
            since: Union[str, datetime] = None,
            until: Union[str, datetime] = None,
            frequency_interval: str = None,
            format: str = None,
            timestamp_format: str = None) -> pd.Series:

        if isinstance(since, str):
            since = iso8601.parse_date(since)

        if isinstance(until, str):
            until = iso8601.parse_date(until)

        if frequency_interval is not None:
            frequency_interval = FrequencyInterval(frequency_interval)

        if format is not None:
            format = Format(format)

        if timestamp_format is not None:
            timestamp_format = TimestampFormat(timestamp_format)

        params = Parameters(asset=asset,
                            since=since,
                            until=until,
                            frequency_interval=frequency_interval,
                            format=format,
                            timestamp_format=timestamp_format)

        return self._get(category, metric, params)

    @classmethod
    def from_env(cls):
        api_key = os.environ.get("GLASSNODE_API_KEY")
        return cls(api_key)
