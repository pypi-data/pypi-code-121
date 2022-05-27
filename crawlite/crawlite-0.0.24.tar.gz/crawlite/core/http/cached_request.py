import requests_cache, uncurl

from crawlite.utils.random import get_random_second
from crawlite.utils.module import FromSettingsMixin

from .utils import set_user_agent
from .exceptions import *
from .adapters import CrawliteFileAdapter
from .helper import trace, retry



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

    
    def get_delay(self, delay):
        if delay is None:
            if isinstance(self.REQUEST_DELAY, (tuple, list,)) and len(self.REQUEST_DELAY) == 2:
                return get_random_second(*self.REQUEST_DELAY)
            return self.REQUEST_DELAY
        return delay
    

    @retry
    @trace
    def fetch(self, method, refresh, delay, proxies=None, logging=True, **kwargs):
        if refresh:
            cache_key = self.requests.cache.create_key(method=method, **kwargs)
            self.requests.cache.delete(cache_key)

        proxies = proxies or self.get_proxies()

        r = self.apply_settings(self.requests.request, setting_prefix='REQUESTS_', method=method, proxies=proxies, **kwargs)
        r.raise_for_status()
        return r
    

    def from_curl(self, command, refresh, delay, proxies=None, logging=True):
        p = uncurl.parse_context(command)
        return self.fetch(
            p.method, refresh, delay, proxies=proxies, logging=logging,
            url=p.url, data=p.data, headers=p.headers, cookies=p.cookies
        )

        
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
    
