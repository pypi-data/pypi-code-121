# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane', 'arcane.spreadsheet']

package_data = \
{'': ['*']}

install_requires = \
['arcane-core>=1.6.0,<2.0.0',
 'arcane-requests>=0.3.0,<0.4.0',
 'google-api-python-client>=2.40.0,<3.0.0',
 'oauth2client==4.1.3']

setup_kwargs = {
    'name': 'arcane-spreadsheet',
    'version': '0.6.1',
    'description': 'Arcane spreadsheet tools',
    'long_description': '# Arcane spreadsheet\n\nUtility package to use google spreadsheet\n',
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
