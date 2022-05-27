import json
from urllib.parse import urljoin

import requests

from . import settings
from .jwt_token_provider import get_jwt_token


__author__ = 'osso'


class LabelPrinterRESTClient(object):
    def __init__(self, base_url, jwt_token):
        self.base_url = base_url
        self.auth_header = {
            'Authorization': 'JWT {0}'.format(jwt_token)}

    def __post_json(self, url, data):
        headers = {'content-type': 'application/json'}
        headers.update(self.auth_header)
        res = requests.post(
            urljoin(self.base_url, url), data=json.dumps(data),
            headers=headers)
        return res

    def get(self, url):
        return self.__get(url)

    def __get(self, url):
        print(urljoin(self.base_url, url))
        res = requests.get(
            urljoin(self.base_url, url), headers=self.auth_header)
        return res

    def __generic_post(self, url, data):
        res = self.__post_json(url, data)
        if res.status_code == 201:
            return res.json()
        else:
            raise Exception(
                "Status code {0}, message {1}".format(
                    res.status_code,
                    res.text))

    def print_generic_label(self, lines):
        return self.__generic_post(
            'api/text_label/',
            {'text': "\n".join(lines)})

    def print_hdd_label(self, hdd_uid, serial_number, owner=''):
        return self.__generic_post(
            'api/hdd_label/',
            {'hdd_uid': hdd_uid,
             'serial_number': serial_number,
             'owner': owner})

    def print_server_label(self, server_uid, name, owner=''):
        return self.__generic_post(
            'api/server_label/',
            {'server_uid': server_uid,
             'name': name,
             'owner': owner})


def get_labelprinter():
    jwt_token = get_jwt_token(
        settings.LABELPRINTER_LOGIN_URL,
        auth_token=settings.LABELPRINTER_AUTH_TOKEN)

    rst = LabelPrinterRESTClient(
        base_url=settings.LABELPRINTER_BASE_URL,
        jwt_token=jwt_token)

    return rst


if __name__ == '__main__':
    rst = get_labelprinter()
    res = rst.get('/api/text_label/')
    assert res.status_code == 405, (res.status_code, res)  # expected
    print(res)
