# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['backtest',
 'backtest.common',
 'backtest.config',
 'backtest.feed',
 'backtest.trade',
 'backtest.web',
 'tests',
 'tests.feed']

package_data = \
{'': ['*'], 'tests': ['data/*', 'packages/*']}

install_requires = \
['Cython>=0.29.28,<0.30.0',
 'aiohttp>=3.8.1,<4.0.0',
 'aioredis==1.3.1',
 'arrow>=0.15.8,<0.16.0',
 'asyncpg>=0.21,<0.22',
 'cfg4py>=0.9.2,<0.10.0',
 'expiringdict>=1.2.1,<2.0.0',
 'fire==0.4.0',
 'gino>=1.0.1,<2.0.0',
 'pandas>=1.4.1,<2.0.0',
 'psutil>=5.9.0,<6.0.0',
 'pyemit==0.4.5',
 'requests>=2.27.1,<3.0.0',
 'sanic>=21.12.1,<22.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'tqdm>=4.63.0,<5.0.0',
 'zillionare-core-types>=0.4.1,<0.5.0',
 'zillionare-omicron>=2.0.0.a29,<3.0.0']

extras_require = \
{'dev': ['black>=22.3.0,<23.0.0',
         'tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.8.0,<4.0.0',
         'pre-commit>=2.17.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['mkdocs>=1.2.3,<2.0.0',
         'mkdocs-include-markdown-plugin>=3.2.3,<4.0.0',
         'mkdocs-material>=8.1.11,<9.0.0',
         'mkdocstrings>=0.18.0,<0.19.0',
         'mkdocs-autorefs>=0.4.1,<0.5.0',
         'Jinja2>=3.0,<3.1',
         'livereload>=2.6.3,<3.0.0'],
 'test': ['isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest==6.1.2',
          'pytest-cov==2.10.1',
          'sanic-testing>=0.8.2,<0.9.0']}

entry_points = \
{'console_scripts': ['bt = backtest.cli:main']}

setup_kwargs = {
    'name': 'zillionare-backtest',
    'version': '0.2.6',
    'description': 'zillionare backtest framework.',
    'long_description': '# zillionare-backtest\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/backtest">\n    <img src="https://img.shields.io/pypi/v/backtest.svg"\n        alt = "Release Status">\n</a>\n\n<a href="https://github.com/zillionare/backtest/actions">\n    <img src="https://github.com/zillionare/backtest/actions/workflows/main.yml/badge.svg?branch=release" alt="CI Status">\n</a>\n\n<a href="https://backtest.readthedocs.io/en/latest/?badge=latest">\n    <img src="https://readthedocs.org/projects/backtest/badge/?version=latest" alt="Documentation Status">\n</a>\n\n</p>\n\n\nbacktest framework\n\n\n* Free software: MIT\n* Documentation: <https://backtest.readthedocs.io>\n\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage) project template.\n',
    'author': 'Aaron Yang',
    'author_email': 'aaron_yang@jieyu.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zillionare/backtest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
