# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pythogen', 'pythogen.parsers']

package_data = \
{'': ['*'], 'pythogen': ['templates/*', 'templates/client/*']}

install_requires = \
['inflection==0.5.1',
 'jinja2==3.1.1',
 'pyyaml==6.0',
 'rich==12.2.0',
 'typer==0.4.1']

setup_kwargs = {
    'name': 'pythogen',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.0,<3.10.0',
}


setup(**setup_kwargs)
