# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gladfull_goldfish']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['gladfull-goldfish = gladfull_goldfish.__main__:main']}

setup_kwargs = {
    'name': 'gladfull-goldfish',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'RincewindWizzard',
    'author_email': 'git@magierdinge.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
