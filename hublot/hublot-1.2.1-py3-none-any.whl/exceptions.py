#!/usr/bin/env python3

# standards
from abc import ABC

# 3rd parties
from requests import RequestException


class ScraperError(ABC, Exception):
    pass


# These are the exceptions that @scraper handles by default. We register them as subclasses of `ScraperError`, as a convenience to
# user code, so that user code doesn't need to import requests just for that exception class.
#
ScraperError.register(ValueError)
ScraperError.register(RequestException)
