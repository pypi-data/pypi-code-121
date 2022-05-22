# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['perm_broker',
 'perm_broker.auth',
 'perm_broker.auth.ops',
 'perm_broker.auth.views',
 'perm_broker.backend',
 'perm_broker.backend.mongodb',
 'perm_broker.backend.mssql',
 'perm_broker.backend.mysql',
 'perm_broker.common',
 'perm_broker.perm',
 'perm_broker.perm.ops',
 'perm_broker.perm.views',
 'perm_broker.user',
 'perm_broker.user.ops',
 'perm_broker.user.views',
 'perm_broker.util']

package_data = \
{'': ['*'], 'perm_broker': ['templates/*']}

setup_kwargs = {
    'name': 'perm-broker',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'Gongziting Tech Ltd.',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
