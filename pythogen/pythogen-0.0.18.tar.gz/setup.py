# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pythogen', 'pythogen.parsers']

package_data = \
{'': ['*'], 'pythogen': ['templates/*', 'templates/client/*']}

install_requires = \
['inflection>=0.5.1,<0.6.0',
 'jinja2>=3.1.1,<4.0.0',
 'pytest>=7.1.2,<8.0.0',
 'pyyaml>=6.0,<7.0',
 'rich>=12.2.0,<13.0.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['pythogen = pythogen.entrypoint:run']}

setup_kwargs = {
    'name': 'pythogen',
    'version': '0.0.18',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/artsmolin/pythogen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
