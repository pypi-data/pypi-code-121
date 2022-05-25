# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wf_airtable_api_schema', 'wf_airtable_api_schema.models']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'wf-airtable-api-schema',
    'version': '0.4.2',
    'description': 'Simple package defining a schema translation layer between the client and Airtable bases',
    'long_description': None,
    'author': 'Benjamin Jaffe-Talberg',
    'author_email': 'ben.talberg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/WildflowerSchools/wf-airtable-api-schema',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
