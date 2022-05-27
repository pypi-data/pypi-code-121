# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['watchmen_data_surface',
 'watchmen_data_surface.cache',
 'watchmen_data_surface.data']

package_data = \
{'': ['*']}

install_requires = \
['watchmen-data-kernel==16.1.4', 'watchmen-rest==16.1.4']

extras_require = \
{'mongodb': ['watchmen-storage-mongodb==16.1.4'],
 'mssql': ['watchmen-storage-mssql==16.1.4'],
 'mysql': ['watchmen-storage-mysql==16.1.4'],
 'oracle': ['watchmen-storage-oracle==16.1.4'],
 'postgresql': ['watchmen-storage-postgresql==16.1.4']}

setup_kwargs = {
    'name': 'watchmen-data-surface',
    'version': '16.1.4',
    'description': '',
    'long_description': None,
    'author': 'botlikes',
    'author_email': '75356972+botlikes456@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
