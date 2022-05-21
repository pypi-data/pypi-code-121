# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiohttp_client_cache',
 'aiohttp_client_cache.backends',
 'aiohttp_client_cache.docs']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp',
 'attrs>=21.2,<22.0',
 'itsdangerous',
 'python-forge>=18.6,<19.0',
 'url-normalize>=1.4,<2.0']

extras_require = \
{'all': ['aioboto3>=9.0',
         'aiobotocore>=2.0',
         'aiofiles>=0.6.0',
         'aiosqlite>=0.16',
         'motor>=2.0',
         'redis>=4.2'],
 'docs': ['furo>=2022.1.2',
          'linkify-it-py>=1.0.1,<2.0.0',
          'myst-parser>=0.15.1,<0.16.0',
          'sphinx>=4.0.2,<5.0.0',
          'sphinx-automodapi>=0.14',
          'sphinx-autodoc-typehints>=1.11,<2.0',
          'sphinx-copybutton>=0.3,<0.4',
          'sphinxcontrib-apidoc>=0.3,<0.4'],
 'docs:python_version >= "3.8"': ['sphinx-inline-tabs>=2022.1.2b11,<2023.0.0'],
 'dynamodb': ['aioboto3>=9.0', 'aiobotocore>=2.0'],
 'filesystem': ['aiofiles>=0.6.0', 'aiosqlite>=0.16'],
 'mongodb': ['motor>=2.0'],
 'redis': ['redis>=4.2'],
 'sqlite': ['aiosqlite>=0.16']}

setup_kwargs = {
    'name': 'aiohttp-client-cache',
    'version': '0.7.0',
    'description': 'Persistent cache for aiohttp requests',
    'long_description': "# aiohttp-client-cache\n\n[![Build status](https://github.com/requests-cache/aiohttp-client-cache/workflows/Build/badge.svg)](https://github.com/requests-cache/aiohttp-client-cache/actions)\n[![Documentation Status](https://img.shields.io/readthedocs/aiohttp-client-cache/stable?label=docs)](https://aiohttp-client-cache.readthedocs.io/en/latest/)\n[![Codecov](https://codecov.io/gh/requests-cache/aiohttp-client-cache/branch/main/graph/badge.svg?token=I6PNLYTILM)](https://codecov.io/gh/requests-cache/aiohttp-client-cache)\n[![PyPI](https://img.shields.io/pypi/v/aiohttp-client-cache?color=blue)](https://pypi.org/project/aiohttp-client-cache)\n[![Conda](https://img.shields.io/conda/vn/conda-forge/aiohttp-client-cache?color=blue)](https://anaconda.org/conda-forge/aiohttp-client-cache)\n[![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/aiohttp-client-cache)](https://pypi.org/project/aiohttp-client-cache)\n[![PyPI - Format](https://img.shields.io/pypi/format/aiohttp-client-cache?color=blue)](https://pypi.org/project/aiohttp-client-cache)\n\n**aiohttp-client-cache** is an async persistent cache for [aiohttp](https://docs.aiohttp.org)\nclient requests, based on [requests-cache](https://github.com/reclosedev/requests-cache).\n\n# Features\n* **Ease of use:** Use as a [drop-in replacement](https://aiohttp-client-cache.readthedocs.io/en/latest/user_guide.html)\n  for `aiohttp.ClientSession`\n* **Customization:** Works out of the box with little to no config, but with plenty of options\n  available for customizing cache\n  [expiration](https://aiohttp-client-cache.readthedocs.io/en/latest/user_guide.html#cache-expiration)\n  and other [behavior](https://aiohttp-client-cache.readthedocs.io/en/latest/user_guide.html#cache-options)\n* **Persistence:** Includes several [storage backends](https://aiohttp-client-cache.readthedocs.io/en/latest/backends.html):\n  SQLite, DynamoDB, MongoDB, and Redis.\n\n# Development Status\n**This library is a work in progress!**\n\nBreaking changes should be expected until a `1.0` release, so version pinning is recommended.\n\nMy goal for this library is to eventually have a similar (but not identical) feature set as\n`requests-cache`, and also contribute new features from this library back to `requests-cache`.\nIf there is a feature you want, if you've discovered a bug, or if you have other general feedback, please\n[create an issue](https://github.com/requests-cache/aiohttp-client-cache/issues/new/choose) for it!\n\n# Quickstart\nFirst, install with pip (python 3.7+ required):\n```bash\npip install aiohttp-client-cache\n```\n\n## Basic Usage\nNext, use [aiohttp_client_cache.CachedSession](https://aiohttp-client-cache.readthedocs.io/en/latest/modules/aiohttp_client_cache.session.html#aiohttp_client_cache.session.CachedSession)\nin place of [aiohttp.ClientSession](https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession).\nTo briefly demonstrate how to use it:\n\n**Replace this:**\n```python\nfrom aiohttp import ClientSession\n\nasync with ClientSession() as session:\n    await session.get('http://httpbin.org/delay/1')\n```\n\n**With this:**\n```python\nfrom aiohttp_client_cache import CachedSession, SQLiteBackend\n\nasync with CachedSession(cache=SQLiteBackend('demo_cache')) as session:\n    await session.get('http://httpbin.org/delay/1')\n```\n\nThe URL in this example adds a delay of 1 second, simulating a slow or rate-limited website.\nWith caching, the response will be fetched once, saved to `demo_cache.sqlite`, and subsequent\nrequests will return the cached response near-instantly.\n\n## Configuration\nSeveral options are available to customize caching behavior. This example demonstrates a few of them:\n\n```python\n# fmt: off\nfrom aiohttp_client_cache import SQLiteBackend\n\ncache = SQLiteBackend(\n    cache_name='~/.cache/aiohttp-requests.db',  # For SQLite, this will be used as the filename\n    expire_after=60*60,                         # By default, cached responses expire in an hour\n    urls_expire_after={'*.fillmurray.com': -1}, # Requests for any subdomain on this site will never expire\n    allowed_codes=(200, 418),                   # Cache responses with these status codes\n    allowed_methods=['GET', 'POST'],            # Cache requests with these HTTP methods\n    include_headers=True,                       # Cache requests with different headers separately\n    ignored_params=['auth_token'],              # Keep using the cached response even if this param changes\n    timeout=2.5,                                # Connection timeout for SQLite backend\n)\n```\n\n# More Info\nTo learn more, see:\n* [User Guide](https://aiohttp-client-cache.readthedocs.io/en/latest/user_guide.html)\n* [Cache Backends](https://aiohttp-client-cache.readthedocs.io/en/latest/backends.html)\n* [API Reference](https://aiohttp-client-cache.readthedocs.io/en/latest/reference.html)\n* [Examples](https://aiohttp-client-cache.readthedocs.io/en/latest/examples.html)\n",
    'author': 'Jordan Cook',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/requests-cache/aiohttp-client-cache',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
