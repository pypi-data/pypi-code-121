# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hotfinger', 'hotfinger.finger_handle_tools']

package_data = \
{'': ['*'], 'hotfinger': ['data/*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'loguru>=0.6.0,<0.7.0',
 'lxml>=4.8.0,<5.0.0',
 'python-Wappalyzer>=0.3.1,<0.4.0',
 'webanalyzer>=2019.8.22,<2020.0.0']

setup_kwargs = {
    'name': 'hotfinger',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'zmf96',
    'author_email': 'zmf96@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
