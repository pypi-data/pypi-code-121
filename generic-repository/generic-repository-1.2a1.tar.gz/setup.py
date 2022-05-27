# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['generic_repository']

package_data = \
{'': ['*']}

modules = \
['py']
extras_require = \
{'http': ['httpx>=0.23.0,<0.24.0'],
 'pydantic': ['pydantic>=1.9.0,<2.0.0'],
 'sqlalchemy': ['SQLAlchemy>=1.4.0,<2.0.0']}

setup_kwargs = {
    'name': 'generic-repository',
    'version': '1.2a1',
    'description': 'Generic repository patterm for python.',
    'long_description': '# Repository pattern for python\n\nThis package includes building blocks to apply repository pattern in your program.\n\n## Usage:\n\nTODO\n',
    'author': 'Francisco Del Roio',
    'author_email': 'francipvb@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
