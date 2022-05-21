# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chalkit']

package_data = \
{'': ['*']}

install_requires = \
['typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['chalkit = chalkit.main:app']}

setup_kwargs = {
    'name': 'chalkit',
    'version': '0.1.0',
    'description': '',
    'long_description': '# CLI to save ideas/todos by just opening your terminal.\n',
    'author': 'Anurag-gg',
    'author_email': 'dsanurag520@gmail.com',
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
