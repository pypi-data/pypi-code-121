# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['watchmen_rest_doll',
 'watchmen_rest_doll.admin',
 'watchmen_rest_doll.analysis',
 'watchmen_rest_doll.auth',
 'watchmen_rest_doll.console',
 'watchmen_rest_doll.gui',
 'watchmen_rest_doll.meta_import',
 'watchmen_rest_doll.sso',
 'watchmen_rest_doll.sso.saml',
 'watchmen_rest_doll.system',
 'watchmen_rest_doll.util']

package_data = \
{'': ['*']}

install_requires = \
['bcrypt>=3.2.0,<4.0.0',
 'passlib>=1.7.4,<2.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'watchmen-data-surface==16.1.4',
 'watchmen-inquiry-surface==16.1.4',
 'watchmen-pipeline-surface==16.1.4']

extras_require = \
{'kafka': ['kafka-python>=2.0.2,<3.0.0', 'aiokafka>=0.7.2,<0.8.0'],
 'mongodb': ['watchmen-storage-mongodb==16.1.4'],
 'mssql': ['watchmen-storage-mssql==16.1.4'],
 'mysql': ['watchmen-storage-mysql==16.1.4'],
 'oracle': ['watchmen-storage-oracle==16.1.4'],
 'postgresql': ['watchmen-storage-postgresql==16.1.4'],
 'prometheus': ['starlette-prometheus>=0.9.0,<0.10.0'],
 'rabbit': ['aio-pika>=7.1.2,<8.0.0'],
 'sso': ['python3-saml>=1.14.0,<2.0.0', 'cryptography>=36.0.2,<37.0.0'],
 'standard_ext_writer': ['requests>=2.27.1,<3.0.0'],
 'trino': ['watchmen-inquiry-trino==16.1.4']}

setup_kwargs = {
    'name': 'watchmen-rest-doll',
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
