# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['htbulma', 'htbulma.services']

package_data = \
{'': ['*']}

install_requires = \
['htag>=0.5,<0.6']

setup_kwargs = {
    'name': 'htbulma',
    'version': '0.5.0',
    'description': 'GUI toolkit for creating beautiful applications for mobile, web, and desktop from a single python3 codebase',
    'long_description': '## htbulma = "HTag bulma"\n\nExemple of gui toolkit using [htag](https://github.com/manatlan/htag).\n\n[available on pypi](https://pypi.org/project/htbulma/)\n\n[See an example](test.py)\n',
    'author': 'manatlan',
    'author_email': 'manatlan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/manatlan/htbulma',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
