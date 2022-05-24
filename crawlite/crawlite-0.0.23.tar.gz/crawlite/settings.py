import os
from datetime import timedelta


# Request
USER_AGENT_NAME = 'chrome'
REQUEST_DELAY = 0.5, 1.5
RETRY_INTERVAL_SECONDS = 10, 15, 20

REQUEST_LOGGING = True


# Request Cache
REQUEST_CACHE_CACHE_NAME = 'crawlite.sqlite'
REQUEST_CACHE_BACKEND = os.environ.get('REQUEST_CACHE_BACKEND', 'sqlite')
REQUEST_CACHE_EXPIRE_AFTER = timedelta(days=100)
REQUEST_CACHE_ALLOWABLE_METHODS = 'GET', 'POST',
REQUEST_CACHE_ALLOWABLE_CODES = 200,
REQUEST_CACHE_OLD_DATA_ON_ERROR = False
REQUEST_CACHE_CACHE_CONTROL = False


# SoupParser
CRAWL_TARGET_ATTRS = ['href', 'src',]
PARSE_CONTENT_TYPES = [
    'text/css', 'text/html', 'text/javascript', 'text/plain', 'text/xml'
]

BS4_FEATURES = 'html.parser'
BS4_PARSE_ONLY = None
BS4_FROM_ENCODING = 'utf-8'
BS4_EXCLUDE_ENCODINGS = None
BS4_ELEMENT_CLASSES = None


EXTRACT_AUTO_STRIP = True
EXTRACT_AUTO_SOUP2TEXT = True

CRAWL_SUSPENDE_LOOP_POLLING_RATE = 1