# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysesame3', 'tests']

package_data = \
{'': ['*'], 'tests': ['fixtures/*']}

install_requires = \
['pycryptodome>=3.14.1,<4.0.0', 'requests>=2.27.1,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=4.2.0,<5.0.0',
                             'importlib-metadata>=4.11.4,<5.0.0'],
 'cognito': ['awsiotsdk>=1.11.1,<2.0.0',
             'boto3>=1.23.6,<2.0.0',
             'certifi',
             'requests-aws4auth>=1.1.2,<2.0.0'],
 'doc': ['livereload>=2.6.3,<3.0.0',
         'mkdocs>=1.3.0,<2.0.0',
         'mkdocstrings>=0.18.1,<0.19.0',
         'mkdocstrings-python>=0.6.6,<0.7.0',
         'mkdocs-autorefs>=0.4.1,<0.5.0',
         'mkdocs-include-markdown-plugin>=3.5.0,<4.0.0',
         'mkdocs-material>=8.2.15,<9.0.0']}

setup_kwargs = {
    'name': 'pysesame3',
    'version': '0.6.0rc1',
    'description': 'Unofficial library to communicate with Sesame smart locks.',
    'long_description': '# pysesame3\n\n_Unofficial Python Library for SESAME products from CANDY HOUSE, Inc._\n\n[![PyPI](https://img.shields.io/pypi/v/pysesame3)](https://pypi.python.org/pypi/pysesame3)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pysesame3)\n![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/mochipon/pysesame3/dev%20workflow/main)\n[![Documentation Status](https://readthedocs.org/projects/pysesame3/badge/?version=latest)](https://pysesame3.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/mochipon/pysesame3/branch/main/graph/badge.svg?token=2Y7OPZTILT)](https://codecov.io/gh/mochipon/pysesame3)\n![PyPI - License](https://img.shields.io/pypi/l/pysesame3)\n\nThis project aims to control SESAME devices by using **[the cloud service](https://doc.candyhouse.co/ja/flow_charts#candy-house-cloud-%E3%81%A8-wifi-module-%E7%B5%8C%E7%94%B1%E3%81%A7-sesame-%E3%82%92%E9%81%A0%E9%9A%94%E6%93%8D%E4%BD%9C)**.\n\n* Free software: MIT license\n* Documentation: [https://pysesame3.readthedocs.io](https://pysesame3.readthedocs.io)\n\n## Supported devices\n\n- [SESAME 3](https://jp.candyhouse.co/products/sesame3)\n- [SESAME 4](https://jp.candyhouse.co/products/sesame4)\n- [SESAME bot](https://jp.candyhouse.co/products/sesame3-bot)\n\n## Features\n\n* Retrieve the device status (battery level, locked, handle position, etc.).\n* Retrieve recent events (locked, unlocked, etc.) associated with a lock.\n* Needless to say, locking, unlocking and clicking (for the bot)!\n\n## Usage\n\nPlease take a look at [the documentation](https://pysesame3.readthedocs.io/en/latest/usage/).\n\n## Related Projects\n\n### Libraries\n| Name | Lang | Communication Method |\n----|----|----\n| [pysesame](https://github.com/trisk/pysesame) | Python | [Sesame API v1/v2](https://docs.candyhouse.co/v1.html)\n| [pysesame2](https://github.com/yagami-cerberus/pysesame2) | Python | [Sesame API v3](https://docs.candyhouse.co/)\n| [pysesame3](https://github.com/mochipon/pysesame3) | Python | [Web API](https://doc.candyhouse.co/ja/SesameAPI), [CognitoAuth (The official android SDK reverse-engineered)](https://doc.candyhouse.co/ja/android)\n| [pysesameos2](https://github.com/mochipon/pysesameos2) | Python | [Bluetooth](https://doc.candyhouse.co/ja/android)\n\n### Integrations\n| Name | Description | Communication Method |\n----|----|----\n| [doorman](https://github.com/jp7eph/doorman) | Control SESAME3 from Homebridge by MQTT | [Web API](https://doc.candyhouse.co/ja/SesameAPI)\n| [Doorlock](https://github.com/kishikawakatsumi/Doorlock) | iOS widget for Sesame 3 smart lock | [Web API](https://doc.candyhouse.co/ja/SesameAPI)\n| [gopy-sesame3](https://github.com/orangekame3/gopy-sesame3) | NFC (Felica) integration | [Web API](https://doc.candyhouse.co/ja/SesameAPI)\n| [homebridge-open-sesame](https://github.com/yasuoza/homebridge-open-sesame) | Homebridge plugin for SESAME3 | Cognito integration\n| [homebridge-sesame-os2](https://github.com/nzws/homebridge-sesame-os2) | Homebridge Plugin for SESAME OS2 (SESAME3) | [Web API](https://doc.candyhouse.co/ja/SesameAPI)\n| [sesame3-webhook](https://github.com/kunikada/sesame3-webhook) | Send SESAME3 status to specified url. (HTTP Post) | CognitoAuth (based on `pysesame3`)\n\n## Credits & Thanks\n\n* A huge thank you to all at [CANDY HOUSE](https://jp.candyhouse.co/) and their crowdfunding contributors!\n* Thanks to [@Chabiichi](https://github.com/Chabiichi)-san for [the offer](https://github.com/mochipon/pysesame3/issues/25) to get my SESAME bot!\n* This project was inspired and based on [tchellomello/python-ring-doorbell](https://github.com/tchellomello/python-ring-doorbell) and [snjoetw/py-august](https://github.com/snjoetw/py-august).\n',
    'author': 'Masaki Tagawa',
    'author_email': 'masaki@tagawa.email',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mochipon/pysesame3',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
