# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['json_de2zh']

package_data = \
{'': ['*']}

install_requires = \
['alive-progress>=2.4.1,<3.0.0',
 'cmat2aset>=0.1.0-alpha.7,<0.2.0',
 'fast-scores>=0.1.2,<0.2.0',
 'fastlid>=0.1.7,<0.2.0',
 'icecream>=2.1.1,<3.0.0',
 'install>=1.3.5,<2.0.0',
 'joblib>=1.1.0,<2.0.0',
 'nltk>=3.7,<4.0',
 'numpy>=1.22.3,<2.0.0',
 'rich>=12.4.1,<13.0.0',
 'set-loglevel>=0.1.2,<0.2.0',
 'simplemma==0.3.0',
 'sklearn>=0.0,<0.1',
 'split-words>=0.1.2,<0.2.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['json-de2zh = json_de2zh.__main__:app']}

setup_kwargs = {
    'name': 'json-de2zh',
    'version': '0.1.1',
    'description': 'pack_name descr ',
    'long_description': '# json-de2zh\n[![pytest](https://github.com/ffreemt/json-de2zh/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/json-de2zh/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/json-de2zh.svg)](https://badge.fury.io/py/json-de2zh)\n\njson-de2zh gen_cmat based on fundset (stardict)\n\n## Install it\n\n```shell\npip install git+https://github.com/ffreemt/json-de2zh\n# poetry add git+https://github.com/ffreemt/json-de2zh\n# git clone https://github.com/ffreemt/json-de2zh && cd json-de2zh\n```\n\n## Use it\n```python\nfrom json_de2zh import json_de2zh\n\n```\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/json-de2zh',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
