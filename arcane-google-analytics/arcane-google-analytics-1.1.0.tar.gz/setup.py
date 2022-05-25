# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane', 'arcane.google_analytics']

package_data = \
{'': ['*']}

install_requires = \
['arcane-core>=1.7.0,<2.0.0',
 'arcane-credentials==0.1.0',
 'arcane-datastore>=1.1.0,<2.0.0',
 'arcane-requests>=0.3.0,<0.4.0',
 'google-api-python-client>=1.7.8',
 'google-auth-httplib2==0.1.0']

setup_kwargs = {
    'name': 'arcane-google-analytics',
    'version': '1.1.0',
    'description': 'A package to use Google Analytics API',
    'long_description': '# Arcane google-analytics\n\nThis package helps us to interact with Google Analytics API\n',
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
