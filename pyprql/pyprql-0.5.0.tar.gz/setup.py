# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyprql', 'pyprql.cli', 'pyprql.magic']

package_data = \
{'': ['*'], 'pyprql': ['assets/*']}

install_requires = \
['Pygments>=2.11.2,<3.0.0',
 'SQLAlchemy>=1.4.32,<2.0.0',
 'click>=8.0.4,<9.0.0',
 'duckdb-engine>=0.1.8,<0.2.0',
 'fuzzyfinder>=2.1.0,<3.0.0',
 'icecream>=2.1.2,<3.0.0',
 'ipython-sql>=0.4.0,<0.5.0',
 'prompt-toolkit>=3.0.28,<4.0.0',
 'prql-python>=0,<1',
 'rich>=12.0.0,<13.0.0',
 'traitlets>=5.2.0,<6.0.0']

extras_require = \
{':python_full_version >= "3.7.1" and python_full_version < "3.8.0"': ['pandas>=1.3,<1.4',
                                                                       'numpy>=1.21,<1.22',
                                                                       'ipython>=7.33.0,<7.34.0'],
 ':python_version >= "3.8" and python_version < "4.0"': ['pandas>=1.4,<2.0',
                                                         'numpy>=1.22.3,<2.0.0',
                                                         'ipython>=8.0,<9.0']}

entry_points = \
{'console_scripts': ['pyprql = pyprql.cli.__init__:main']}

setup_kwargs = {
    'name': 'pyprql',
    'version': '0.5.0',
    'description': 'Python Implementation of Pipelined Relational Query Language (PRQL)',
    'long_description': '# PyPrql\n\n[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)\n![PyPI - License](https://img.shields.io/pypi/l/pyprql)\n![PyPI](https://img.shields.io/pypi/v/pyprql)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyprql)\n\n[![Documentation Status](https://readthedocs.org/projects/pyprql/badge/?version=latest)](https://pyprql.readthedocs.io/en/latest/?badge=latest)\n![Discord](https://img.shields.io/discord/936728116712316989)\n![GitHub contributors](https://img.shields.io/github/contributors/prql/pyprql)\n![GitHub Repo stars](https://img.shields.io/github/stars/prql/pyprql)\n\n[![CI/CD](https://github.com/prql/PyPrql/actions/workflows/cicd.yaml/badge.svg?branch=main)](https://github.com/prql/PyPrql/actions/workflows/cicd.yaml)\n[![codecov](https://codecov.io/gh/prql/PyPrql/branch/main/graph/badge.svg?token=C6J2UI7FR5)](https://codecov.io/gh/prql/PyPrql)\n\n[![Codestyle: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n\nPython bindings to [PRQL][prql].  Documentation of PRQL is [here][prql_docs].\n\nThis project is maintained by [@qorrect](https://github.com/qorrect/) and [@rbpatt2019](https://github.com/rbpatt2019)\n\n## Installation\n\n```bash\npip install pyprql\n```\n\n### Try it out\n\n#### Database\n\n```bash\ncurl https://github.com/qorrect/PyPrql/blob/main/resources/chinook.db?raw=true -o chinook.db\npyprql "sqlite:///chinook.db"\n\nPRQL> show tables\n```\n\n#### CSV file\n\n```bash\ncurl https://people.sc.fsu.edu/~jburkardt/data/csv/zillow.csv\npyprql zillow.csv\n```\n\n### The pyprql tool\n\n* pyprql can connect to any database that SQLAlchemy supports, execute `pyprql` without arguments for docs on how to install drivers.\n* pyprql can connect to CSV files,  replace the connection string with the file path and it will load the CSV into a temporary SQLite database.\n* pyprql can save the results with a ` | to csv ${filename}` transform at the end of the query\n* pyprql has auto-completion on table names and table aliases with _tab_, and history-completion with _alt-f_\n\n[prql]: https://github.com/prql/prql\n[prql_docs]: https://lang.prql.builders/introduction.html\n',
    'author': 'qorrect',
    'author_email': 'charlie.fats@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/prql/PyPrql',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
