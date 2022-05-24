import urllib.error as urllib2
import urllib.request as urllib
import time

from functools import wraps


def retry(exception_to_check, tries=3, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param exception_to_check: the exception to check. may be a tuple of
        exceptions to check
    :type exception_to_check: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
                    print(e)
                    if hasattr(e, 'code') and e.code == 404:
                        msg = "%s. Aborting" % (str(e))
                        mtries = mdelay = 0
                    else:
                        msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)

                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)

                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


@retry(urllib2.URLError, tries=3, delay=3, backoff=2)
def download(uri, http_proxy=None, https_proxy=None, wait_secs=.5):
    time.sleep(wait_secs)
    proxy_def = {}
    protocol = uri[0:uri.index(':')]

    if protocol == 'http' and http_proxy:
        proxy_def['http'] = http_proxy
    elif protocol == 'https' and https_proxy:
        proxy_def['https'] = https_proxy

    # set the proxy if any
    if len(proxy_def.keys()):
        proxy = urllib.ProxyHandler(proxy_def)
        opener = urllib.build_opener(proxy)
        urllib.install_opener(opener)

    return urllib.urlopen(uri)

