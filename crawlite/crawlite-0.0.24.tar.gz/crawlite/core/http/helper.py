import functools, time
from collections import abc

from .exceptions import RetryMaxCountDone



def transform_bytes_length(length, ndigits=None):
    k = 1024
    m = k**2
    g = k**3

    if length > k:
        unit = 'K'
        v = length / k
    elif length > m:
        unit = 'M'
        v = length / m
    elif length > g:
        unit = 'G'
        v = length / g
    else:
        unit = 'bytes'
        v = length
    return f'{round(v, ndigits)}{unit}'


def _get_pre_request_log(method, url, data=None, proxies=None, **extra):
    METHOD = method.upper()

    PROXIES = f"Proxy:{proxies}" if proxies else ''
    
    prefix = ' '.join(filter(None, [METHOD, url, PROXIES]))

    PAYLOADS = f"payloads:{transform_bytes_length(payloads, 2)}" if (data:=data) and (payloads := len(data)) else ''
    
    if postfix:= list(filter(None, [PAYLOADS])):
        postfix = ', '.join(postfix)
        postfix = f' ({postfix})'
    else:
        postfix = ''

    log = f"{prefix}{postfix}"
    return log


def _get_after_request_log(response, delay, elasped):
    content_length = len(response.content or '')
    status = response.status_code
    size_exp = transform_bytes_length(content_length)
    log = f'{status} {size_exp} {elasped}s'

    if ctype:= response.headers.get('Content-Type'):
        log = f'{log} {ctype}'

    if response.from_cache:
        log = f'{log} (From Cache)'
    else:
        log = f'{log} (delay:{delay or 0}s)'
    return log


def trace(func):
    @functools.wraps(func)
    def wrapper(self, method, refresh, delay,**kwargs):
        try:
            pre_log = _get_pre_request_log(method, **kwargs)
            print(pre_log, '\r', end='', sep='...')
            st = time.time()
            r = func(self, method, refresh, delay, **kwargs)
            et = time.time()
            elapsed = round(et-st, 2)
            log = f'{pre_log} => {_get_after_request_log(r, delay, elapsed)}'
            print(log)
            if not r.from_cache:
                time.sleep(delay)
        except Exception as e:
            print(e)
        else:
            return r
    return wrapper



def retry(func):
    @functools.wraps(func)
    def wrapper(self, *args,**kwargs):
        url = kwargs.get('url')
        if isinstance(self.RETRY_INTERVAL_SECONDS, abc.Iterable):
            retry_seconds = list(self.RETRY_INTERVAL_SECONDS)
        elif isinstance(self.RETRY_INTERVAL_SECONDS, (int, float,)):
            retry_seconds = [self.RETRY_INTERVAL_SECONDS]
        elif not hasattr(self, 'RETRY_INTERVAL_SECONDS'):
            retry_seconds = []
        else:
            raise ValueError(f'RETRY_INTERVAL_SECONDS must be integer float or iterables not {self.RETRY_INTERVAL_SECONDS}')

        retry_proxies = list(self.proxies_list) or [None]

        for i, sec in enumerate(retry_seconds):
            for proxies in retry_proxies:
                try:
                    r = func(self, *args, **kwargs)
                except Exception as e: 
                    print(f"Exception: {e.__class__.__name__}")
                    print(f" - {e.args[0]}")
                    if proxies:
                        if (next_proxies := self.rotate_proxies()) != proxies:
                            print(f" - The requests by pass proxy server {proxies} has failed. Trying to next proxy server {next_proxies}")
                            time.sleep(1)
                else:
                    return r
            print(f" - Request {url} Failed, retry after {sec}sec(trys: {i+1})")
            time.sleep(sec)
        else:
            raise RetryMaxCountDone(f'Request {url} Failed!')
    return wrapper
