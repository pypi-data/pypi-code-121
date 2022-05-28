# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dzbee']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'Morfessor>=2.0.6,<3.0.0',
 'XlsxWriter>=3.0.3,<4.0.0',
 'aset2pairs>=0.1.0,<0.2.0',
 'cchardet>=2.1.7,<3.0.0',
 'icecream>=2.1.1,<3.0.0',
 'install>=1.3.5,<2.0.0',
 'json-de2zh>=0.1.1,<0.2.0',
 'logzero>=1.7.0,<2.0.0',
 'polyglot>=16.7.4,<17.0.0',
 'typer>=0.4.1,<0.5.0']

extras_require = \
{'plot': ['holoviews>=1.14.9,<2.0.0',
          'plotly>=5.8.0,<6.0.0',
          'seaborn>=0.11.2,<0.12.0']}

entry_points = \
{'console_scripts': ['dzbee = dzbee.__main__:app']}

setup_kwargs = {
    'name': 'dzbee',
    'version': '0.1.1a3',
    'description': 'pack_name descr ',
    'long_description': '# dzbee\n[![pytest](https://github.com/ffreemt/dzbee/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/dzbee/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8%2B&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/dzbee.svg)](https://badge.fury.io/py/dzbee)\n\nAlign german(de)-chinese(zh) texts, fast\n\n### Python 3.8 Only\n\n## Pre-Install `fasttext`, `pycld2`, `PyICU`\n*   If your computer **does not** have a C++ compiler,\n search for needed wheels at  https://www.lfd.uci.edu/~gohlke/pythonlibs/ and install, e.g.,\n    ```\n     pip install fasttext-0.9.2-cp38-cp38-win_amd64.whl pycld2-0.41-cp38-cp38-win_amd64.whl PyICU-2.8.1-cp38-cp38-win_amd64.whl\n    ```\n*   If your computer *does* have a C++ compiler\n    ```\n       pip insall fasttext pycld2 PyICU\n       # poetry add fasttext pycld2 PyICU\n    ```\n\n## Install it\n\n```shell\npip install dzbee\n\n# poetry add dzbee\n# pip install git+https://github.com/ffreemt/dzbee\n# poetry add git+https://github.com/ffreemt/dzbee\n# git clone https://github.com/ffreemt/dzbee && cd dzbee\n```\n\n## Use it\n```bash\ndzbee file1 file2\n\n```\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/dzbee',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
