import hashlib
import json
import uuid
from typing import List

import requests


class RequestsClient:

    @staticmethod
    def filter(data):
        if isinstance(data, (list, tuple, dict)):
            data = json.dumps(data, ensure_ascii=False)
        return data.encode()

    @staticmethod
    def get(url: str, headers: dict = None, timeout: int = 30):
        if not headers:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
        elif 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json; charset=utf-8'
        r = requests.get(
            url,
            headers=headers,
            timeout=timeout
        )
        try:
            return r.json()
        except Exception as e:
            print(e)
            return r.content.decode()

    def post(self, xml, url: str, headers: dict = None, timeout: int = 30):
        xml = self.filter(xml)
        if not headers:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
        elif 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json; charset=utf-8'
        post_params = dict(
            url=url,
            headers=headers,
            data=xml,
            timeout=timeout
        )

        r = requests.post(**post_params)
        try:
            return r.json()
        except Exception as e:
            print(e)
            return r.content.decode()


def md5(s: str) -> str:
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


def gen_uuid() -> str:
    return str(uuid.uuid4())


def get_padding_line(text: str, max_len: int = None, padding: str = None) -> str:
    """
    add padding to log text
    "some logs"  ==> "-------- some logs --------"

    :param text: log text
    :param max_len: padding len
    :param padding: padding character, default: -
    :return:
    """
    max_len = max_len or 60
    padding = padding or '-'

    text_len = len(text)
    if (text_len % 2) == 0:
        _size = (max_len - text_len) // 2
        side_str = padding * _size
        return f"{side_str} {text} {side_str}"
    else:
        _size = (max_len - text_len) // 2
        side_str = padding * _size
        return f"{side_str}{padding} {text} {side_str}"


def printl(data: str):
    print(get_padding_line(data))


def convert_dict_key(data_dict: dict, rule: dict) -> dict:
    if data_dict and rule:
        for k, v in rule.items():
            if k in data_dict:
                data_dict[v] = data_dict.pop(k)
    return data_dict


def convert_list_dict_key(data_list: List[dict], rule: dict) -> list:
    if data_list and rule:
        for data_item in data_list:
            for k, v in rule.items():
                if k in data_item:
                    data_item[v] = data_item.pop(k)
    return data_list


def sqlescape(s: str):
    return s.translate(
        s.maketrans({
            "\0": "\\0",
            "\r": "\\r",
            "\x08": "\\b",
            "\x09": "\\t",
            "\x1a": "\\z",
            "\n": "\\n",
            "\"": "",
            "'": "",
            "\\": "\\\\",
            "%": "\\%"
        })
    )
