# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_eventdone']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nonebot-plugin-eventdone',
    'version': '0.1.8',
    'description': '',
    'long_description': None,
    'author': 'Padro Felice',
    'author_email': '2659737583@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
