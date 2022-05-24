# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['people_analytics_itsm_sdk',
 'people_analytics_itsm_sdk.sdk',
 'people_analytics_itsm_sdk.sdk.servicenow',
 'people_analytics_itsm_sdk.sdk.servicenow.attachments',
 'people_analytics_itsm_sdk.sdk.servicenow.helpers',
 'people_analytics_itsm_sdk.sdk.servicenow.table']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'people-analytics-itsm-sdk',
    'version': '0.0.13',
    'description': 'O Itsm é utilizado para facilitar as integrações e também a reutilização de código',
    'long_description': None,
    'author': 'Stone People Analytics',
    'author_email': 'systems-techpeople@stone.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
