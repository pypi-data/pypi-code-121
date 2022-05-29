# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beancount_ce']

package_data = \
{'': ['*']}

install_requires = \
['beancount>=2.2,<3.0',
 'pdfminer.six>=20200726,<20200727',
 'regex>=2020.7.14,<2021.0.0']

setup_kwargs = {
    'name': 'beancount-ce',
    'version': '1.0.4',
    'description': "Beancount statements (pdf and csv) importer for Caisse d'Epargne bank",
    'long_description': "# Beancount Caisse d'Epargne Importer\n\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/ArthurFDLR/beancount-ce/beancount-ce?style=for-the-badge)](https://github.com/ArthurFDLR/beancount-ce/actions)\n[![PyPI](https://img.shields.io/pypi/v/beancount-ce?style=for-the-badge)](https://pypi.org/project/beancount-ce/)\n[![PyPI - Version](https://img.shields.io/pypi/pyversions/beancount-ce.svg?style=for-the-badge)](https://pypi.org/project/beancount-ce/)\n[![GitHub](https://img.shields.io/github/license/ArthurFDLR/beancount-ce?style=for-the-badge)](https://github.com/ArthurFDLR/beancount-ce/blob/master/LICENSE.txt)\n[![Linting](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)\n\n`beancount-ce` provides a statements (PDF and CSV) importer for the bank [Caisse d'Epargne](http://www.caisse-epargne.fr) to the [Beancount](http://furius.ca/beancount/) format.\n\n## Installation\n\n```console\n    $ pip install beancount-ce\n```\n\n## Usage\n\nAdd ```CEImporter``` to your [Beancount importers config file](https://beancount.github.io/docs/importing_external_data.html#configuration).\n\n```python\n    IBAN_NUMBER_CE = 'FR00 1111 2222 3333 4444 5555 666'\n\n    CONFIG = [\n        CEImporter(\n            iban=IBAN_NUMBER_CE,\n            account='Assets:FR:CdE:CompteCourant',\n            expenseCat='Expenses:FIXME',    #Optional\n            creditCat='Income:FIXME',       #Optional\n            showOperationTypes=False        #Optional\n        ),\n    ]\n```\n\n## Contribution\n\nFeel free to contribute!\n\nPlease make sure you have Python 3.6+ and [`Poetry`](https://poetry.eustace.io/) installed.\n\n1. Git clone the repository - `git clone https://github.com/ArthurFDLR/beancount-ce`\n\n2. Install the packages required for development - `poetry install`\n\n3. That's basically it. You should now be able to run lint checks and the test suite - `make lint test`.\n",
    'author': 'Arthur Findelair',
    'author_email': 'arthfind@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ArthurFDLR/beancount-ce',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
