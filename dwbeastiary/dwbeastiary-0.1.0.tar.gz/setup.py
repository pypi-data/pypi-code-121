# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dwbeastiary']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['beastiary = dwbeastiary:main']}

setup_kwargs = {
    'name': 'dwbeastiary',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Chris Blades',
    'author_email': 'chrisdblades@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
