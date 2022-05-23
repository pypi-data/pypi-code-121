import requests
from wiliot.cloud_apis.security import security
import json
import logging
import urllib.parse
import os

log_level = logging.INFO


class WiliotCloudError(Exception):
    pass


class Client:
    def __init__(self, oauth_username, oauth_password, env='', log_file=None, logger_= None):
        if oauth_password is None:
            raise Exception('oauth_password cannot be None')
        if oauth_username is None:
            raise Exception('oauth_username cannot be None')
        self.env = env+"/" if env != '' else ''
        api_path = "https://api.wiliot.com/{env}v1/".format(env=self.env)
        self.base_path = api_path + self.client_path
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        self.auth_obj = security.WiliotAuthentication(api_path, oauth_username, oauth_password)
        self.headers["Authorization"] = self.auth_obj.get_token()
        if logger_ is None:
            self.logger = logging.getLogger()
            self.logger.setLevel(log_level)
        else:
            self.logger = logging.getLogger(logger_)

        if not self.logger.hasHandlers():
            if log_file is not None:
                self.handler = logging.FileHandler(log_file)
            else:
                self.handler = logging.StreamHandler()
            self.handler.setLevel(log_level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.handler.setFormatter(formatter)
            self.logger.addHandler(self.handler)

    def _get(self, path, params=None):
        response = requests.get(self.base_path+path, headers=self.headers, params=params)
        message = response.json()
        if isinstance(message, str):
            message = {"data": message}
        message.update({'status_code': response.status_code})
        if response.status_code != 200:
            raise WiliotCloudError(message)
        return message

    def _put(self, path, payload):
        response = requests.put(self.base_path+urllib.parse.quote(path), headers=self.headers, data=json.dumps(payload))
        message = response.json()
        if isinstance(message,str):
            message = {"data":message}
        message.update({'status_code':response.status_code})
        if response.status_code != 200:
            raise WiliotCloudError(message)
        return message

    def _post(self, path, payload, params=None, files=None):
        response = requests.post(self.base_path+urllib.parse.quote(path), headers=self.headers,
                                 data=json.dumps(payload) if payload is not None else None,
                                 params=params)
        message = response.json()
        if isinstance(message,str):
            message = {"data":message}
        message.update({'status_code':response.status_code})
        if response.status_code != 200:
            raise WiliotCloudError(message)
        return message

    def _post_with_files(self, path, files, payload=None, params=None):
        if payload is None:
            payload = {}
        self.headers.pop('Content-Type')
        response = requests.request("POST", self.base_path+urllib.parse.quote(path), headers=self.headers,
                                    data=payload,
                                    params=params,
                                    files=files)
        message = response.json()
        if isinstance(message, str):
            message = {"data": message}
        message.update({'status_code': response.status_code})
        if response.status_code != 200:
            raise WiliotCloudError(message)
        return message

    def _delete(self, path, payload=None):
        response = requests.delete(self.base_path + urllib.parse.quote(path), headers=self.headers,
                                   data=json.dumps(payload) if payload is not None else None)
        if response.status_code != 200:
            raise WiliotCloudError(response.text)
        message = response.json()
        return message
