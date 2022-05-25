# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['waj_bigquery',
 'waj_bigquery.core',
 'waj_bigquery.core.bigquery',
 'waj_bigquery.tests']

package_data = \
{'': ['*'], 'waj_bigquery.core': ['models/*']}

install_requires = \
['google-cloud-bigquery>=3.0.1,<4.0.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'waj-bigquery',
    'version': '0.2.2',
    'description': '',
    'long_description': None,
    'author': 'Gabriel González',
    'author_email': 'gabriel@whaleandjaguar.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
