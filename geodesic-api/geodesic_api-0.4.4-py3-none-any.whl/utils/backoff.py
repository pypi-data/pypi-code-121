import os
import warnings

try:
    import tenacity
except ImportError:
    warnings.warn("'tenacity' not installed, backoff will not be used on certain remote calls")
    tenacity = None

import logging

retries = int(os.getenv("GEODESIC_BACKOFF_RETRIES", 10))

if tenacity is None:
    def backoff(f):
        return f
else:
    def backoff(f):
        """
        Decorates function f with a backoff with our chosen defaults. If you want
        to customize, just use tenacity directly...
        """

        logger = logging.getLogger(__name__)
        dec = tenacity.retry(
            wait=tenacity.wait_exponential(multiplier=1, min=1, max=64) + tenacity.wait_random(0, 1),
            stop=tenacity.stop_after_attempt(retries),
            after=tenacity.after_log(logger, logging.WARNING),
            retry=tenacity.retry_if_result(lambda x: x is None) | tenacity.retry_if_exception_type()
        )

        return dec(f)
