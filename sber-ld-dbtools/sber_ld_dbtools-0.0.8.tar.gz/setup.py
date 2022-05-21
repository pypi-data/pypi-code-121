# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sber_ld_dbtools',
 'sber_ld_dbtools.credentials',
 'sber_ld_dbtools.loader',
 'sber_ld_dbtools.loader.greenplum',
 'sber_ld_dbtools.loader.oracle',
 'sber_ld_dbtools.loader.spark',
 'sber_ld_dbtools.loader.spark.hive',
 'sber_ld_dbtools.loader.teradata']

package_data = \
{'': ['*']}

install_requires = \
['JPype1>=1,<2',
 'JayDeBeApi>=1,<2',
 'pandakeeper>=0.0.27,<0.0.28',
 'pandas>=1,<2',
 'psycopg2-binary>=2,<3',
 'pyspark>=2,<3',
 'teradatasql>=17,<18',
 'varutils>=0.0.8,<0.0.9']

setup_kwargs = {
    'name': 'sber-ld-dbtools',
    'version': '0.0.8',
    'description': 'Tools for interacting with LD databases.',
    'long_description': '# sber_ld_dbtools\nTools for interacting with LD databases.\n',
    'author': 'Andrew Sonin',
    'author_email': 'sonin.cel@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrewsonin/sber_ld_dbtools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
