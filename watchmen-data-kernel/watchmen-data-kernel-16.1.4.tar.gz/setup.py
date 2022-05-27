# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['watchmen_data_kernel',
 'watchmen_data_kernel.cache',
 'watchmen_data_kernel.common',
 'watchmen_data_kernel.encryption',
 'watchmen_data_kernel.external_writer',
 'watchmen_data_kernel.meta',
 'watchmen_data_kernel.service',
 'watchmen_data_kernel.storage',
 'watchmen_data_kernel.storage_bridge',
 'watchmen_data_kernel.topic_schema',
 'watchmen_data_kernel.utils']

package_data = \
{'': ['*']}

install_requires = \
['cacheout>=0.13.1,<0.14.0',
 'pycryptodome>=3.14.1,<4.0.0',
 'watchmen-meta==16.1.4']

extras_require = \
{'mongodb': ['watchmen-storage-mongodb==16.1.4'],
 'mssql': ['watchmen-storage-mssql==16.1.4'],
 'mysql': ['watchmen-storage-mysql==16.1.4'],
 'oracle': ['watchmen-storage-oracle==16.1.4'],
 'postgresql': ['watchmen-storage-postgresql==16.1.4']}

setup_kwargs = {
    'name': 'watchmen-data-kernel',
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
