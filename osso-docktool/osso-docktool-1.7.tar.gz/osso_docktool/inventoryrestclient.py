import json

import requests

try:
    from urllib.parse import urljoin  # py3
except ImportError:
    from urlparse import urljoin  # py2

from . import settings
from .jwt_token_provider import get_jwt_token, is_expired

__author__ = 'osso'


class InventoryRESTClient(object):
    def __init__(self, base_url):
        self.base_url = urljoin(base_url, '/api/')
        self.hdd_uid = None
        self.__jwt_token = None

    @property
    def auth_header(self):
        if self.__jwt_token:
            if is_expired(self.__jwt_token):
                self.__jwt_token = None
        if not self.__jwt_token:
            self.__jwt_token = get_jwt_token(
                settings.DASHBOARD_SCHEME_URL,
                settings.DASHBOARD_AUTH_TOKEN)
        return {'Authorization': 'JWT {0}'.format(self.__jwt_token)}

    def __post_json(self, url, data):
        headers = {'content-type': 'application/json'}
        headers.update(self.auth_header)
        res = requests.post(
            urljoin(self.base_url, url), data=json.dumps(data),
            headers=headers)
        return res

    def __patch_json(self, url, data):
        headers = {'content-type': 'application/json'}
        headers.update(self.auth_header)
        res = requests.patch(
            urljoin(self.base_url, url),
            data=json.dumps(data),
            headers=headers)
        return res

    def get(self, url):
        return self.__get(url)

    def __get(self, url):
        res = requests.get(
            urljoin(self.base_url, url),
            headers=self.auth_header)
        return res

    def __generic_patch(self, url, data):
        res = self.__patch_json(url, data)
        if res.status_code != 200:
            raise Exception(
                'Status code {}, message {}, when trying to PATCH {}'.format(
                    res.status_code, res.text, data))
        return res.json()

    def __generic_post(self, url, data):
        res = self.__post_json(url, data)
        if res.status_code not in (200, 201):
            raise Exception(
                'Status code {}, message {}, when trying to POST {}'.format(
                    res.status_code, res.text, data))
        return res.json()

    def get_last_owner(self, asset_id):
        res = self.__get(
            'assets/asset_owner/?asset={0}&order_by=-date&limit=1'.format(
                asset_id)
        )
        if res.status_code not in (200, 400):
            raise Exception('Status code {}, message {} for {}'.format(
                res.status_code, res.text, asset_id))

        if res.status_code == 400:
            return None
        data = res.json()
        if not data:
            return None
        return data[0]['name']

    def get_hdd_url(self, asset_id):
        return urljoin(self.base_url, '/app/assets/disks/{}/'.format(
            asset_id))

    def get_hdd(self, asset_id):
        res = self.__get(
            'assets/hdd/?id={0}'.format(
                asset_id)
        )
        if res.status_code == 200:
            data = res.json()
            if not data:
                return None
            return data
        elif res.status_code == 400:
            return None
        else:
            raise Exception('Status code {0}, message {1}'.format(
                res.status_code, res.text))

    def change_bay(self, hdd_id, bay):
        return self.__generic_patch(
            'assets/hdd/{0}/?update_bay'.format(hdd_id),
            {'bay': bay})

    def add_owner(self, hdd_id, name, email=' '):
        return self.__generic_patch(
            'assets/hdd/{0}/?update_owner'.format(hdd_id),
            {'name': name,
             'email': email})

    def add_location(self, hdd_id, location):
        return self.__generic_patch(
            'assets/hdd/{0}/?update_location'.format(hdd_id),
            {'location': location})

    def add_status(self, hdd_id, status, extra_info=' '):
        return self.__generic_patch(
            'assets/hdd/{0}/?update_status'.format(hdd_id),
            {'status': status,
             'extra_info': extra_info})

    def add_health_status(self, hdd_id, status, extra_info=' '):
        return self.__generic_patch(
            'assets/hdd/{0}/?update_health'.format(hdd_id),
            {'status': status,
             'extra_info': extra_info})

    def add_wbpclass(self, hdd_id, wbp_class_number, extra_info=' '):
        return self.__generic_patch(
            'assets/hdd/{0}/?update_wbpclass'.format(hdd_id),
            {'wbp_class_number': wbp_class_number,
             'extra_info': extra_info})

    def add_smart_data(self, hdd_id, rawdata):
        return self.__generic_post(
            'assets/hdd_smartdata/',
            {'data': rawdata,
             'hdd': hdd_id})

    def add_hdd(self, hdd_dock, bay='', asset_uid=None):
        data = {
            'device_model': hdd_dock.get_device_model(),
            'serial_number': hdd_dock.get_serial_number(),
            'user_capacity': hdd_dock.get_user_capacity(),
            'ata_version': hdd_dock.get_ata_version(),
            'firmware_version': hdd_dock.get_firmware_version(),
            'smart_status': hdd_dock.get_smart_status(),
            'bay': bay,
        }

        if hdd_dock.get_model_family():
            data['model_family'] = hdd_dock.get_model_family()

        return self.__generic_post('api/assets/hdd/', data)

    def get_hdd_id(self, device_model, serial_number):
        assert '\n' not in str(device_model) + str(serial_number)
        assert '&' not in str(device_model) + str(serial_number)

        if device_model:
            res = self.__get(
                'assets/hdd/?serial_number={0}&device_model={1}'.format(
                    serial_number, device_model))
        else:
            res = self.__get(
                'assets/hdd/?limit=2&offset=0&overview=True&search={}'.format(
                    serial_number))
            if res.status_code != 200:
                raise Exception('Status code {0}, message {1}'.format(
                    res.status_code, res.text))
            data = res.json()
            if data['count'] > 1:
                raise Exception('Multiple results: {}'.format(data))
            if data['count'] == 0:
                return None
            return data['results'][0]['id']

        if res.status_code == 200:
            data = res.json()
            if not data:
                return None
            return data[0]['id']
        else:
            raise Exception('Status code {0}, message {1}'.format(
                res.status_code, res.text))
