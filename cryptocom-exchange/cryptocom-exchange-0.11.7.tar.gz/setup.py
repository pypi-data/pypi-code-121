# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cryptocom', 'cryptocom.exchange']

package_data = \
{'': ['*']}

install_requires = \
['aiolimiter>=1.0.0,<2.0.0',
 'async-timeout>=4.0.2,<5.0.0',
 'cached-property>=1.5.2,<2.0.0',
 'httpx>=0.22.0,<0.23.0',
 'websockets>=10.3,<11.0']

setup_kwargs = {
    'name': 'cryptocom-exchange',
    'version': '0.11.7',
    'description': 'Python 3.7+ async library for crypto.com/exchange API using httpx and websockets',
    'long_description': "# Python 3.7+ async library for crypto.com/exchange API using httpx and websockets\n\n[![Docs Build Status](https://readthedocs.org/projects/cryptocom-exchange/badge/?version=latest&style=flat)](https://readthedocs.org/projects/cryptocom-exchange)\n![Test workflow](https://github.com/goincrypto/cryptocom-exchange/actions/workflows/test.yml/badge.svg)\n[![Maintainability](https://api.codeclimate.com/v1/badges/8d7ffdae54f3c6e86b5a/maintainability)](https://codeclimate.com/github/goincrypto/cryptocom-exchange/maintainability)\n[![Test Coverage](https://api.codeclimate.com/v1/badges/8d7ffdae54f3c6e86b5a/test_coverage)](https://codeclimate.com/github/goincrypto/cryptocom-exchange/test_coverage)\n[![PyPI implementation](https://img.shields.io/pypi/implementation/cryptocom-exchange.svg)](https://pypi.python.org/pypi/cryptocom-exchange/)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/cryptocom-exchange.svg)](https://pypi.python.org/pypi/cryptocom-exchange/)\n[![PyPI license](https://img.shields.io/pypi/l/cryptocom-exchange.svg)](https://pypi.python.org/pypi/cryptocom-exchange/)\n[![PyPI version fury.io](https://badge.fury.io/py/cryptocom-exchange.svg)](https://pypi.python.org/pypi/cryptocom-exchange/)\n[![PyPI download month](https://img.shields.io/pypi/dm/cryptocom-exchange.svg)](https://pypi.python.org/pypi/cryptocom-exchange/)\n[![Gitter](https://badges.gitter.im/goincrypto/cryptocom-exchange.svg)](https://gitter.im/goincrypto/cryptocom-exchange?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)\n\nDocumentation: [https://cryptocom-exchange.rtfd.io](https://cryptocom-exchange.rtfd.io)\n\nExchange original API docs: [https://exchange-docs.crypto.com](https://exchange-docs.crypto.com)\n\n### **WARNING: PLEASE use 0.10.3+ [prev versions have private websocket broken and memory leaks]\n\n### Description\n\n`pip install cryptocom-exchange`\n\n- provides all methods to access crypto.com/exchange API (except for websockets temporary)\n- full test coverage on real exchange with real money\n- simple async methods with custom retries and timeouts\n\n**Please do not use secret keys, they used only for test purposes**\n\n### Changelog\n\n- **0.10.4** - Updated pairs\n- **0.10.3** - fixed websocket private endpoints not returning data\n- **0.10.2** - fixed huge memory leak by `httpx`\n- [leaks memory] **0.10.1** - added read timeouts for websockets, fixed test with tickers\n- [leaks memory] **0.10.0** - moved into httpx + websockets, added autoreconnect, simplified code, improved stability\n- **0.9.5** - added timeout for websocket if no data received in 3 mins we trying to reconnect\n- **0.9.4** - fixed spread func, fixed missing params\n- **0.9.3** - added RPS limiter by @Irishery\n- **0.9.2** - fixed event loop import level\n- **0.9.1** - fixed Windows bug with asyncio event loop\n- **0.9.0** - updated coins, refactored wallet transactions\n- **0.8.1** - fixed coin name generation\n- **0.8** - fixed tests with updated coins\n- **0.7.12** - updated coins, added websocket timeouts\n- **0.7.11** - fixed orders history if empty\n- **0.7.10** - updated pairs precision\n- **0.7.9** - fixed price and quantity rounding, updated pairs and coins\n- **0.7.8** - changed keys, removed depth from orderbook (not working, always 150), updated pairs\n- **0.7.7** - updated pairs by JOB, fixed timeout\n- **0.7.6** - updated pairs\n- **0.7.5** - fixed `order.remaining_quantity` rounding\n- **0.7.4** - fixed sync pairs for account\n- **0.7.3** - fixed price of order if not filled, updated coins, added missing trades to `Order`\n- **0.7.2** - fixed `listen_orders` private account method, added test\n- **0.7.1** - fixed missing '.0' in order price and quantity (different in py3.7, py3.9)\n- **0.7** - major changes, `Pair` -> `cro.pairs.CRO_USDT` moved to more complex structure so we can use round and server information about pairs.\n    - If you have errors, just use `await account.sync_pairs()` or `await exchange.sync_pairs()`\n    - Added rounding per pair, all floats will be with right precisions\n- **0.6** - included changes from PR kudos to https://github.com/samueltayishere, fixed limit orders, fixed timeouts, fixed is_active order status\n- **0.5.1** - added symbols YFI, BAND, fixed test with limit orders\n- **0.5** - missing symbols MKR, UNI, possible refactoring for simple objects\n- **0.4.5** - fixed missing CELR balances\n- **0.4.4** - fixed missing QTUM, CELR coins\n- **0.4.3** - fixed missing `fees_coin` Coin enum\n- **0.4.2** - fixed supported pairs OMG and MANA\n- **0.4.1** - fixed `cached_property` for python 3.7\n- **0.4.0** - added `OrderForceType` and `OrderExecType`, refactored `Order` responses, splited private and market methods, added missing `Pair` and `Coin`, added `Balance` dataclass, public\nkeys for tests passing\n- **0.3.4** - fixed balances listener, fixed pairs\n- **0.3.3** - fixed orderbook depth\n- **0.3.2** - added orderbook websocket method\n- **0.3.1** - fixed missing DAI pair\n- **0.3** - added websocket support for public endpoints and supports `sign=True` for private endpoints\n- **0.2.1** - fixed order_id in `get_order` func, still preparing for stable release\n- **0.2** - moved to new API v2, except for websockets\n",
    'author': 'Morty Space',
    'author_email': 'morty.space@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
