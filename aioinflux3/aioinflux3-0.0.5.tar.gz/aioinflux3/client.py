import logging
import httpx
import urllib
import time
import datetime
import numpy as np
from typing import List
from aioinflux3.line_protocal import Measurement, QueryBody, Query

UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
UTF_SHORT_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def strptime(time_str):
    dt, tm = time_str.split('T')
    y, m, d = dt.split('-')
    seconds, ms = tm.split('.')
    h, min, sec = seconds.split(':')
    micro = ms.lower().replace('z', '')[:6]
    return datetime.datetime(year=int(y), month=int(m), day=int(d), hour=int(h), minute=int(min), second=int(sec), microsecond=int(micro))


class InfluxClient:
    def __init__(self, host:str = '127.0.0.1', port: int = 8086, token: str = '', bucket: str = '', org: str = ''):
        self.url_base = f'http://{host}:{port}/api/v2'
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Token {token}"
        }
        self.bucket = bucket
        self.org = org
        self.cols = []

    def query_string(self):
        return urllib.parse.urlencode({
            'bucket': self.bucket,
            'org': self.org,
            'precision': 'ms'
        })

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def url_for(self, path: str) -> str:
        return f"{self.url_base}{path}?{self.query_string()}"

    async def write(self, data: Measurement):
        post_url = self.url_for('/write')
        logging.error('will post to:%s', post_url)
        async with httpx.AsyncClient() as client:
            resp = await client.post(post_url, content=data.serialize(), headers=self.headers)
            logging.error(resp.text)

    def table_response(self, lines: List[str]) -> dict:
        header = lines.pop(0).split(',')[2:]
        tbody = []
        for row in lines:
            cols = [col.strip() for col in row.split(',')[2:]]
            tbody.append(cols)
        return dict(header=header, tbody=tbody)

    def _trans_value(self, val, idx, dtype):
        tp = dtype[idx]
        if tp == 'int64':
            return int(val)
        if tp == 'float64' or tp == 'float32':
            return float(val)
        return val

    def numpy_response(self, lines: List[str]) -> np.ndarray:
        lines.pop(0)
        dtype = [('ts', 'float32')]
        for col in self.cols:
            dtype.append((col, 'float64'))

        data_table = []
        data_length = 0
        for _idx, row in enumerate(lines):
            columns = [_c.strip() for _c in row.split(',')]
            if len(columns) < 2:
                continue
            _tb_index = int(columns[2])

            _dt = strptime(columns[5]) if len(
                columns[5]) > 20 else datetime.datetime.strptime(columns[5], UTF_SHORT_FORMAT)
            _ts = time.mktime(_dt.timetuple()) + float("0.%s" % _dt.microsecond)

            _v = columns[6]
            _f = columns[7]
            # logging.error(f'{_f} = {_v}')
            data_row = [_ts]
            for _ in self.cols:
                data_row.append(0)

            if _tb_index == 0:
                data_row[1] = float(_v)
                data_table.append(data_row)
                data_length += 1
            else:
                _current_idx = _idx % data_length
                data_table[_current_idx][_tb_index + 1] = float(_v)
        return np.array([tuple(_r) for _r in data_table], dtype=dtype)
        #return data_table

    async def query(self, query: Query, numpy=False):
        post_url = self.url_for('/query')
        body = QueryBody(params={}, query=query.to_query())
        logging.error("query:\n%s", body)
        self.cols = query.cols
        async with httpx.AsyncClient() as client:
            resp = await client.post(post_url, json=body.serialize(), headers=self.headers)
            lines = resp.text.split('\r\n')
            #print(lines)
            if numpy:
                return self.numpy_response(lines)
            else:
                return self.table_response(lines)
