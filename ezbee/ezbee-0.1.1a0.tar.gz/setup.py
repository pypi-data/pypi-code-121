# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ezbee']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.1,<4.0.0',
 'Morfessor>=2.0.6,<3.0.0',
 'XlsxWriter>=3.0.3,<4.0.0',
 'cchardet>=2.1.7,<3.0.0',
 'cmat2aset==0.1.0a7',
 'environs>=9.5.0,<10.0.0',
 'fast-scores==0.1.3a3',
 'icecream>=2.1.1,<3.0.0',
 'install>=1.3.5,<2.0.0',
 'logzero>=1.7.0,<2.0.0',
 'polyglot>=16.7.4,<17.0.0',
 'typer>=0.4.0,<0.5.0']

extras_require = \
{'plot': ['holoviews>=1.14.8,<2.0.0',
          'plotly>=5.6.0,<6.0.0',
          'seaborn>=0.11.2,<0.12.0']}

entry_points = \
{'console_scripts': ['ezbee = ezbee.__main__:app']}

setup_kwargs = {
    'name': 'ezbee',
    'version': '0.1.1a0',
    'description': 'engnlish-chinese dualtext aligner',
    'long_description': '# ezbee\n[![pytest](https://github.com/ffreemt/ezbee/actions/workflows/windows-pytest.yml/badge.svg)](https://github.com/ffreemt/ezbee/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8%2B&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/ezbee.svg)](https://badge.fury.io/py/ezbee)\n\nezbee to align en/zh texts\n\n## Install it\n\n```shell\npip install git+https://github.com/ffreemt/ezbee\n# poetry add git+https://github.com/ffreemt/ezbee\n# git clone https://github.com/ffreemt/ezbee && cd ezbee\n```\n\n## Use it\n```python\nezbee --help\n# or python -m ezbee --help\n```\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/ezbee',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
