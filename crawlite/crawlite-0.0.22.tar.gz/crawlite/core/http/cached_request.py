from logging import warning
import time
from warnings import warn
import requests_cache

from crawlite.utils.random import get_random_second
from crawlite.utils.module import FromSettingsMixin

from .utils import retry, set_user_agent
from .exceptions import *
from .adapters import CrawliteFileAdapter


class CachedRequests(FromSettingsMixin):
    HEADERS = None
    COOKIES = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {}
        self.cookies = {}
        self.proxies_list = []
        self.headers = self.apply_settings(set_user_agent, header=self.headers)
        
        if self.HEADERS:
            self.headers.update(self.HEADERS)
        if self.COOKIES:
            self.cookies.update(self.COOKIES)

        if hasattr(self, 'PROXIES_LIST'):
            self.proxies_list = self.PROXIES_LIST
        
        self.requests = self.apply_settings(
            requests_cache.CachedSession,
            setting_prefix='REQUEST_CACHE_'
        )
        self.requests.mount('file:///', CrawliteFileAdapter())

    def get_request_log(self, method, url, from_cache, delay, payloads=None, proxies=None):
        METHOD = 'GET'
        if method == 'post':
            METHOD = "POST"

        PROXIES = ''
        if proxies:
            PROXIES = f"Proxy:{proxies}"
        
        FROM_CACHE = ''
        DELAY = ''
        if from_cache is True:
            FROM_CACHE = 'From Cache'
        else:
            DELAY = f"delay:{delay}s"

        prefix = ' '.join(filter(None, [METHOD, url, PROXIES, FROM_CACHE]))

        PAYLOADS = ''
        if payloads is not None:
            PAYLOADS = f"payloads:{payloads}"
        
        if postfix:= list(filter(None, [DELAY, PAYLOADS])):
            postfix = ', '.join(postfix)
            postfix = f' ({postfix})'
        else:
            postfix = ''

        log = f"{prefix}{postfix}"

        return log

    def _refresh_cache(self, url, method='get'):
        if method == 'get':
            if self.requests.cache.has_url(url):
                self.requests.cache.delete_url(url)
        else:
            self.requests.remove_expired_responses()

    def _delay_control(self, response, delay):
        if response.from_cache is False:
            delay = self._get_delay(delay)
            time.sleep(delay)
            return delay

    def _get_delay(self, delay):
        if delay is None:
            if isinstance(self.REQUEST_DELAY, (tuple, list,)) and len(self.REQUEST_DELAY) == 2:
                return get_random_second(*self.REQUEST_DELAY)
            return self.REQUEST_DELAY
        return delay

    def _validate_response(self, response):
        pass
        if not response.content:
            self.requests.cache.delete_url(response.url)
            warning(f'Warning: {response.url} has no content!')
            
    
    @retry
    def get(self, url, refresh, delay=None, **kwargs):
        if refresh:
            self._refresh_cache(url)
        proxies = self.get_proxies()
        r = self.apply_settings(
            self.requests.get, url, setting_prefix='REQUESTS_', proxies=proxies, **kwargs
        )
        r.raise_for_status()
        delay = self._delay_control(r, delay)
        if self.REQUEST_LOGGING is True:
            log = self.get_request_log('get', url, r.from_cache, delay, proxies=proxies)
            print(log)
        return r

    @retry
    def post(self, url, data, delay=None, **kwargs):
        proxies = self.get_proxies()
        r = self.apply_settings(
            self.requests.post, url, setting_prefix='REQUESTS_', data=data, proxies=proxies, **kwargs
        )
        r.raise_for_status()
        delay = self._delay_control(r, delay)
        if self.REQUEST_LOGGING is True:
            log = self.get_request_log('post', url, r.from_cache, delay, len(data or b''), proxies=proxies)
            print(log)
        return r
        
    def get_headers(self):
        return dict(self.headers)

    def set_header(self, headers):
        self.headers = headers
    
    def get_cookies(self):
        return dict(self.cookies)
    
    def set_cookies(self, cookies):
        self.cookies = cookies

    def get_proxies(self):
        for proxies in self.proxies_list:
            return proxies
    
    def rotate_proxies(self):
        if self.proxies_list:
            h, *r = self.proxies_list
            self.proxies_list = [*r, h]
            return self.proxies_list[0]
    
