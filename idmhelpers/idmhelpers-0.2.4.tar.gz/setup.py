# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['idmhelpers']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'idmhelpers',
    'version': '0.2.4',
    'description': 'Helper library for common Databricks activities for Data Engineering, Delta Tables, Pipelines',
    'long_description': None,
    'author': 'divyavanmahajan',
    'author_email': 'divya.mahajan@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
