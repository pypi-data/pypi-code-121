# -*- coding: utf-8 -*-

import requests

from tuxsuite.cli.version import __version__


def headers(config):
    return {
        "User-Agent": f"tuxsuite.cli/{__version__}",
        "Authorization": config.token,
    }


def apiurl(config, url):
    return f"{config.tuxapi_url}{url}"


def get(config, url, params=None):
    # print(f"GET {config.tuxapi_url}{url} {params=}")
    return requests.get(
        f"{config.tuxapi_url}{url}", headers=headers(config), params=params
    )


def post(config, url, data):
    # print(f"POST {config.tuxapi_url}{url}")
    # print(f"POST {data}")
    return requests.post(
        f"{config.tuxapi_url}{url}", headers=headers(config), json=data
    )
