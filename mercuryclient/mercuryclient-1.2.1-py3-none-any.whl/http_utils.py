import logging

import requests

logger = logging.getLogger(__name__)


def log_response_time(r, *args, **kwargs):
    """
    Hook to log response time
    :param r:
    :param args:
    :param kwargs:
    :return:
    """
    # log in Milliseconds
    logger.info(
        "Mercury {},{},{},{}".format(
            r.request.method,
            r.url,
            r.status_code,
            int(r.elapsed.total_seconds() * 1000),
        )
    )


def get_session():
    """
    Build Mercury Session
    :return:
    """
    s = requests.Session()
    s.hooks["response"].append(log_response_time)
    return s
