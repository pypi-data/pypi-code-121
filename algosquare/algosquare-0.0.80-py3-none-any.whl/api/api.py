from abc import ABC, abstractmethod

import re
import time
import functools
import pandas as pd

import requests

BASE_URL = 'https://api.algosquare.ai/api'

class ApiObject(ABC):
    def __init__(self, entry):
        if type(self) == ApiObject:
            raise RuntimeError('base class should not be instantiated')

        for k, v in entry.items():
            if k.startswith('time_'):
                setattr(self, k, pd.to_datetime(v))
            else:
                setattr(self, k, v)

    def __str__(self):
        return str(self.__dict__)

    def update(self, entry):
        for k, v in entry.items():
            if k.startswith('time_'):
                setattr(self, k, pd.to_datetime(v))
            else:
                setattr(self, k, v)

class AuthenticationError(Exception):
    pass

class ApiError(Exception):
    pass

def check_api_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from .. import API_KEY

        if API_KEY is None:
            raise ValueError('API_KEY is not set')
        if not isinstance(API_KEY, str):
            raise TypeError('API_KEY must be a string')
        if len(API_KEY) != 64:
            raise ValueError('API_KEY must be 64 characters')

        r = func(API_KEY, *args, **kwargs)
        
        if r.status_code == 403:
            raise AuthenticationError(r.text)
        if not r.ok:
            raise ApiError(r.text)

        return r.json()
    return wrapper

def urljoin(*args):
    return '/'.join(args)

def fullurl(url):
    return urljoin(BASE_URL, url)

@check_api_call
def api_get(api_key, url):
    return requests.get(fullurl(url), headers=dict(Authorization = api_key))

@check_api_call
def api_post(api_key, url, **kwargs):
    return requests.post(fullurl(url), headers=dict(Authorization = api_key), **kwargs)

@check_api_call
def api_put(api_key, url, **kwargs):
    return requests.put(fullurl(url), headers=dict(Authorization = api_key), **kwargs)

@check_api_call
def api_delete(api_key, url):
    return requests.delete(fullurl(url), headers=dict(Authorization = api_key))
