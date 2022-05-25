# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ebooks_lister', 'tests']

package_data = \
{'': ['*']}

extras_require = \
{':extra == "test"': ['ebooklib>=0.17.1,<0.18.0', 'black>=22.3.0,<23.0.0'],
 'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocstrings>=0.15.2',
         'mkdocs-autorefs>=0.2.1,<0.3.0'],
 'test': ['isort>=5.8.0,<6.0.0',
          'flake8>=3.9.2,<4.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'mypy>=0.900,<0.901',
          'pytest>=6.2.4,<7.0.0',
          'pytest-cov>=2.12.0,<3.0.0']}

entry_points = \
{'console_scripts': ['ebooks-lister = ebooks_lister.cli:main']}

setup_kwargs = {
    'name': 'ebooks-lister',
    'version': '0.1.0',
    'description': 'Get normalized metadata from paths with ebooks.',
    'long_description': '# eBooks Lister\n\n\n[![pypi](https://img.shields.io/pypi/v/ebooks-lister.svg)](https://pypi.org/project/ebooks-lister/)\n[![python](https://img.shields.io/pypi/pyversions/ebooks-lister.svg)](https://pypi.org/project/ebooks-lister/)\n[![Build Status](https://github.com/mattkatz/ebooks-lister/actions/workflows/dev.yml/badge.svg)](https://github.com/mattkatz/ebooks-lister/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/mattkatz/ebooks-lister/branch/main/graphs/badge.svg)](https://codecov.io/github/mattkatz/ebooks-lister)\n\n\n\nGet normalized metadata from paths with ebooks\n\n\n* Documentation: <https://mattkatz.github.io/ebooks-lister>\n* GitHub: <https://github.com/mattkatz/ebooks-lister>\n* PyPI: <https://pypi.org/project/ebooks-lister/>\n* Free software: MIT\n\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n',
    'author': 'Matt Katz',
    'author_email': 'projects@morelightmorelight.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mattkatz/ebooks-lister',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
