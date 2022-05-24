# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['arkhamdb']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'httpx>=0.22.0,<0.23.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.11.3,<5.0.0']}

entry_points = \
{'console_scripts': ['arkhamdb = arkhamdb.console:main']}

setup_kwargs = {
    'name': 'arkhamdb',
    'version': '0.0.4',
    'description': 'Pythonic wrapper around the excellent ArkhamDB API. Designed to be standalone and importable to other projects.',
    'long_description': '# python-arkhamdb\n\n[![status-badge](https://ci.jamesveitch.xyz/api/badges/james/python-arkhamdb/status.svg)](https://ci.jamesveitch.xyz/james/python-arkhamdb)[![Read the Docs](https://readthedocs.org/projects/arkhamdb/badge/)](https://arkhamdb.readthedocs.io/)\n\nPythonic wrapper around the excellent [ArkhamDB API](https://arkhamdb.com/api/). Designed to be standalone and importable to other projects.\n\n![Logo](docs/assets/logo-small.png)\n',
    'author': 'James Veitch',
    'author_email': '1722315+darth-veitcher@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
