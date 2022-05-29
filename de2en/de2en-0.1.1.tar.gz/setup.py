# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['de2en']

package_data = \
{'': ['*']}

install_requires = \
['dzbee>=0.1.1-alpha.2,<0.2.0',
 'ezbee>=0.1.1,<0.2.0',
 'icecream>=2.1.1,<3.0.0',
 'install>=1.3.5,<2.0.0',
 'logzero>=1.7.0,<2.0.0',
 'word2word>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'de2en',
    'version': '0.1.1',
    'description': 'pack_name descr ',
    'long_description': '# de2en\n[![pytest](https://github.com/ffreemt/de2en/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/de2en/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8%2B&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/de2en.svg)](https://badge.fury.io/py/de2en)\n\nde2en and gen_cmat\n\n## Install it\n\n```shell\npip install de2en\n\n# poetry add de2en\n# pip install git+https://github.com/ffreemt/de2en\n# poetry add git+https://github.com/ffreemt/de2en\n# git clone https://github.com/ffreemt/de2en && cd de2en\n```\n\n## Use it\n```python\nfrom de2en import de2en\n\n```\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/de2en',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
