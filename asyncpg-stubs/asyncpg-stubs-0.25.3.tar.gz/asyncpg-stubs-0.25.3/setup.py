# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncpg-stubs']

package_data = \
{'': ['*'],
 'asyncpg-stubs': ['_testbase/*',
                   'exceptions/*',
                   'pgproto/*',
                   'protocol/*',
                   'protocol/codecs/*']}

install_requires = \
['asyncpg>=0.25.0,<0.26.0', 'typing-extensions>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'asyncpg-stubs',
    'version': '0.25.3',
    'description': 'asyncpg stubs',
    'long_description': '# asyncpg-stubs\n\n[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/bryanforbes/asyncpg-stubs/blob/master/LICENSE)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n[![Checked with pyright](https://img.shields.io/badge/pyright-checked-informational.svg)](https://github.com/microsoft/pyright/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nThis package contains type stubs to provide more precise static types and type inference for [asyncpg](https://github.com/MagicStack/asyncpg).\n\n## Installation\n\n```shell\npip install asyncpg-stubs\n```\n\n## Development\n\nMake sure you have [poetry](https://python-poetry.org/) installed.\n\n```shell\npoetry install\npoetry run pre-commit install --hook-type pre-commit\n```\n\n## Version numbering scheme\n\nThe **major** and **minor** version numbers of `asyncpg-stubs` will match the **major**\nand **minor** version numbers of the `asyncpg` release the stubs represent. For\ninstance, if you are using `asyncpg` version `0.25.0`, you would use `asyncpg-stubs`\nversion `0.25.X` where `X` is the latest **patch** version of the stubs. Using semver\ndependencty specifications, `asyncpg-stubs` version `~0.25` is designed to work with\n`asyncpg` version `~0.25`.\n\nIn addition, `asyncpg-stubs` will indicate which versions of the runtime library are compatible through its dependency information (as suggested in PEP-561).\n',
    'author': 'Bryan Forbes',
    'author_email': 'bryan@reigndropsfall.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bryanforbes/asyncpg-stubs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
