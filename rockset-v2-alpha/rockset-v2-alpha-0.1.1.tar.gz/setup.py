# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rockset', 'rockset.api', 'rockset.apis', 'rockset.model', 'rockset.models']

package_data = \
{'': ['*']}

install_requires = \
['geojson>=2.5.0,<3.0.0',
 'python_dateutil>=2.5.3,<3.0.0',
 'urllib3>=1.25.3,<2.0.0']

setup_kwargs = {
    'name': 'rockset-v2-alpha',
    'version': '0.1.1',
    'description': 'The python client for the Rockset API.',
    'long_description': "Official Rockset Python Client\n==============================\n\nA Python library for Rockset's API.\n\n\nSetup\n-----\n\nYou can install this package by using the pip tool and installing:\n\n    $ pip install rockset-v2-alpha\n\n\nUsing the Rockset API\n---------------------\n\nDocumentation for this library can be found here:\n\n- https://rockset.com/docs/client/python/ (these docs are still the old ones)\n",
    'author': 'Rockset',
    'author_email': 'support@rockset.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rockset/rockset-python-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
