# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gvol']

package_data = \
{'': ['*']}

install_requires = \
['gql[requests]==3.0.0rc0']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['typing-extensions>=4.0.1,<5.0.0'],
 'docs': ['sphinx>=4.3.2,<5.0.0', 'sphinx-rtd-theme>=1.0.0,<2.0.0']}

setup_kwargs = {
    'name': 'gvol',
    'version': '0.3.1',
    'description': 'GVol is a Python library to access the GVol API',
    'long_description': '# GVol\n\n[![Latest Version](https://img.shields.io/pypi/v/gvol.svg)](https://pypi.org/project/gvol/)\n[![Supported Python Versions](https://img.shields.io/pypi/pyversions/gvol.svg)](https://pypi.org/project/gvol/)\n[![Main Workflow](https://github.com/genesis-volatility/gvol-py/actions/workflows/main.yml/badge.svg)](https://github.com/genesis-volatility/gvol-py/actions/workflows/main.yml)\n[![Documentation Status](https://readthedocs.org/projects/gvol/badge/?version=latest)](https://gvol.readthedocs.io/en/latest/?badge=latest)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nGVol is a Python library to access the [GVol API](https://docs.gvol.io/).\n\n---\n\n**Documentation**: [https://gvol.readthedocs.io/en/latest/index.html](https://gvol.readthedocs.io/en/latest/index.html)\n\n---\n\n## Install\n\n```bash\npip install gvol\n```\n\n## Demo\n\n```python\nfrom gvol import GVol\n#Valid Headers: "x-oracle", "gvol-lite", "gvol-lite-plus"\ngvol_client = GVol(header="gvol-lite", gvol_api_key="ENTER YOUR API KEY HERE")\n\norderbook_skew_strike = gvol_client.CurrentOrderbookSkewStrike(\n    symbol="BTC", exchange="deribit"\n)\n\nprint(orderbook_skew_strike)\n```\n',
    'author': 'Denys Halenok',
    'author_email': 'denys.halenok@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/genesis-volatility/gvol-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
