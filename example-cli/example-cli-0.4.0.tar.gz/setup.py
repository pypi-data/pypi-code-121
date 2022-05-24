# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['example_cli']

package_data = \
{'': ['*']}

install_requires = \
['Gooey>=1.0.8,<2.0.0', 'aiohttp>=3.8.1,<4.0.0']

entry_points = \
{'console_scripts': ['example-cli = example_cli.__main__:main',
                     'sunrise-cli = example_cli.sunrise:main']}

setup_kwargs = {
    'name': 'example-cli',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'RincewindWizzard',
    'author_email': 'git@magierdinge.de',
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
