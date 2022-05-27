# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['debee']

package_data = \
{'': ['*']}

install_requires = \
['aset2pairs>=0.1.0,<0.2.0',
 'cmat2aset==0.1.0a7',
 'de2en>=0.1.1-alpha.1,<0.2.0',
 'fast-scores>=0.1.2,<0.2.0',
 'fastlid>=0.1.7,<0.2.0',
 'icecream>=2.1.1,<3.0.0',
 'install>=1.3.5,<2.0.0',
 'logzero>=1.7.0,<2.0.0',
 'set-loglevel>=0.1.2,<0.2.0',
 'simplemma>=0.3.0,<0.4.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['debee = debee.__main__:app']}

setup_kwargs = {
    'name': 'debee',
    'version': '0.1.0a1',
    'description': 'pack_name descr ',
    'long_description': '# debee\n[![pytest](https://github.com/ffreemt/debee/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/debee/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8%2B&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/debee.svg)](https://badge.fury.io/py/debee)\n\ndebee descr\n\n## Install it\n\n```shell\npip install git+https://github.com/ffreemt/debee\n# poetry add git+https://github.com/ffreemt/debee\n# git clone https://github.com/ffreemt/debee && cd debee\n```\n\n## Use it\n```python\nfrom debee import debee\n\n```\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/debee',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
