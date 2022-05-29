# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['litbee']

package_data = \
{'': ['*']}

install_requires = \
['cchardet>=2.1.7,<3.0.0',
 'debee>=0.1.0-alpha.2,<0.2.0',
 'dzbee>=0.1.1-alpha.2,<0.2.0',
 'ezbee>=0.1.0,<0.2.0',
 'icecream>=2.1.1,<3.0.0',
 'install>=1.3.5,<2.0.0',
 'loguru>=0.6.0,<0.7.0',
 'logzero>=1.7.0,<2.0.0',
 'set-loglevel>=0.1.2,<0.2.0',
 'streamlit-aggrid>=0.2.3,<0.3.0',
 'streamlit-multipage>=0.0.18,<0.0.19',
 'streamlit>=1.9.2,<2.0.0']

entry_points = \
{'console_scripts': ['litbee = litbee.__main__:app']}

setup_kwargs = {
    'name': 'litbee',
    'version': '0.1.1',
    'description': 'align (en, de, zh) texts via streamlit ',
    'long_description': "# litbee\n[![pytest](https://github.com/ffreemt/litbee/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/litbee/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/litbee.svg)](https://badge.fury.io/py/litbee)\n\nlitbee (currently with ezbee, dzbee and debee), made with streamlit\n\n## Pre-install\nPython 3.8 only\n\n`pyicu`, `pycld2` and `fasttext`: refer to `debee`'s pre-install [https://github.com/ffreemt/debee/blob/main/README.md](https://github.com/ffreemt/debee/blob/main/README.md)\n\n## via pip\n```bash\npip install litbee\npython -m litbee\n```\n\n## Or via git clone\n```\ngit clone https://github.com/ffreemt/litbee\ncd litbee\n```\n\n## Install it\n```shell\npoetry install\n\n# or pip install -r requirements.txt\n```\n\n## Use it\n```bash\npython -m streamlit run app.py\n\n# or streamlit run app.py\n# or python -m litbee\n```\n",
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/litbee',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
