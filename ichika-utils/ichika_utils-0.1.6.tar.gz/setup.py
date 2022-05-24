# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ichika_utils']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.2,<4.0.0',
 'pandas>=1.4.2,<2.0.0',
 'scikit-learn>=1.1.1,<2.0.0',
 'scipy>=1.8.0,<2.0.0',
 'uvloop>=0.16.0,<0.17.0']

setup_kwargs = {
    'name': 'ichika-utils',
    'version': '0.1.6',
    'description': 'Asynchronous Statistics Utils for Ichika',
    'long_description': '<div align=center>\n\n# Ichika Utils\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ichika-utils?label=Python&logo=python&logoColor=white) ![PyPI](https://img.shields.io/pypi/v/ichika-utils?label=PyPi&logo=pypi&logoColor=white) ![PyPI - Downloads](https://img.shields.io/pypi/dd/ichika-utils?label=Downloads&logo=pypi&logoColor=white) [![CodeQL](https://github.com/No767/Ichika-Utils/actions/workflows/codeql.yml/badge.svg)](https://github.com/No767/Ichika-Utils/actions/workflows/codeql.yml) [![Snyk](https://github.com/No767/Ichika-Utils/actions/workflows/snyk.yml/badge.svg)](https://github.com/No767/Ichika-Utils/actions/workflows/snyk.yml) [![Bandit](https://github.com/No767/Ichika-Utils/actions/workflows/bandit.yml/badge.svg)](https://github.com/No767/Ichika-Utils/actions/workflows/bandit.yml) ![GitHub](https://img.shields.io/github/license/No767/Ichika-Utils?label=License&logo=github)\n\nAsynchronous Statistics Utils for Ichika\n\n<div align=left>\n\n# Info\n\nThis is a set of utils for Ichika, and this is not even production ready. This is highly experimental.\n',
    'author': 'No767',
    'author_email': '73260931+No767@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/No767/Ichika-Utils',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
