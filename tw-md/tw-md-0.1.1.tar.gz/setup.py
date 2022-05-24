# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tw_md', 'tw_md.domain', 'tw_md.errors', 'tw_md.service']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['tw-md = tw_md.cli:cli']}

setup_kwargs = {
    'name': 'tw-md',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Cleyson Lima',
    'author_email': 'cleysonph@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
