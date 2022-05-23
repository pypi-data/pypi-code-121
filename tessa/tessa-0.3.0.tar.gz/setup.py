# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tessa']

package_data = \
{'': ['*']}

install_requires = \
['frozendict>=2.3.1,<3.0.0',
 'investpy>=1.0.8,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'pycoingecko>=2.2.0,<3.0.0']

setup_kwargs = {
    'name': 'tessa',
    'version': '0.3.0',
    'description': 'Find financial assets and get their price history without worrying about different APIs or rate limiting.',
    'long_description': '\n# tessa\n\n### Find financial assets and get their price history without worrying about different APIs or rate limiting.\n\ntessa is a small package to help you **easily search asset identifiers** (e.g., tickers) and\n**retrieve price information** for assets in different categories such as stocks,\ncrypto, etfs, etc.\n\ntessa builds on investpy and pycoingecko and offers **a simplified and somewhat unified\ninterface**. This applies especially to investpy, which for some reason has different ways\nof finding assets and accessing the respective data.\n\nWhy these two packages? [investpy](https://github.com/alvarobartt/investpy) offers\nhigh-quality data for most categories from [investing.com](https://www.investing.com/).\nHowever, investing.com lacks on the crypto side, so crypto data is retrieved using\n[pycoingecko](https://github.com/man-c/pycoingecko) from\n[Coingecko](https://www.coingecko.com/)\'s API.\n\nImportantly, tessa makes sure to be nice to the sites being accessed and tries to\n**prevent users from being blocked by 429 rate limiting errors** by 1) caching results upon\nretrieval and 2) keeping track of request timestamps and waiting appropriate amounts of\ntime if necessary.\n\n# Main functions\n\n- `search`: Search for an asset in all sources and types.\n- `price_history`: Retrieve the full history of an asset as a dataframe.\n- `price_point_strict`: Get an asset\'s price at a certain point in time. Fail if no\n  price found.\n- `price_point`: Same, but find the nearest price if the given point in time has no\n  price.\n- `price_latest`: Get an asset\'s latest price.\n\n# Usage examples\n\n```python\n>>> from tessa import price_history, search, price_point, price_latest\n\n# Ex 1, easy – Get straightforward price information:\n>>> df, currency = price_history("AAPL", "stock", "united states")\n>>> price_point("SAPG", "stock", "2015-12-25", "germany" )\n# (Will return price at 2015-12-23.)\n>>> price_point_strict("SAPG", "stock", "2015-12-25", "germany" )\n# (Will raise a KeyError.)\n>>> price_latest("ethereum", "crypto")\n\n# Ex 2, medium – Find ticker and get price information for some \n# lesser-known stock, e.g. the original Roche:\n>>> res = search("roche", "switzerland")\n    2 of investing_stocks_by_full_name\n    2 of investing_stocks_by_name\n    1 of investing_funds_by_name\n    ...\n>>> res["investing_stocks_by_name"]\n# -> Ticker is ROG\ndf, currency = price_history("ROG", "stock", country="switzerland")\n\n# Ex 3, medium – Find Coingecko id and get price information for a\n# more obscure token:\n>>> res = search("jenny")\n    1 of coingecko_other_symbol\n    2 of coingecko_other_name\n>>> res["coingecko_other_name"]\n# ...\n>>> df, currency = price_history("jenny-metaverse-dao-token", "crypto")\n\n# Ex 4, medium – Find an ETF:\n>>> res = search("carbon")\n# ...\n>>> res["investing_etfs_by_full_name"]\n# ...\n>>> df, currency = price_history("VanEck Vectors Low Carbon Energy", "etf", "united states")\n\n# Ex 5, medium – Search in a selection of countries and products:\n>>> res = search("renewable", countries=["united states", "canada", "mexico"], products=["etfs", "funds", "indices"])\n# ...\n\n# Ex 6, advanced – Find a stock that is not (yet?) exposed on investpy:\n>>> price_history("PINS", "stock", "united states")\n# Produces an error\n>>> res = search("pinterest")\n    2 of investing_searchobj_other\n>>> res["investing_searchobj_other"]\n[\'{"id_": 1127189, "name": "Pinterest Inc", "symbol": "PINS", "country": "united states", "tag": "/equities/pinterest-inc", "pair_type": "stocks", "exchange": "NYSE"}\',\n \'{"id_": 1177341, "name": "Pinterest Inc", "symbol": "PINS-RM", "country": "russia", "tag": "/equities/pinterest-inc?cid=1177341", "pair_type": "stocks", "exchange": "Moscow"}\']\n >>> df, currency = price_history(res["investing_searchobj_other"][0], "searchobj")\n # ...\n```\n\n\n# How to install\n\npip install tessa\n\n\n# Prerequisites\n\nSee `pyproject.toml`. Major prerequisites are the `investpy` and `pycoingecko` packages.\n\n\n# Future Work\n\nThis if an initial version. There are a number of ideas on how to extend. Please leave\nyour suggestions and comments in the [Issues\nsection](https://github.com/ymyke/tessa/issues).\n',
    'author': 'ymyke',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ymyke/tessa',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
