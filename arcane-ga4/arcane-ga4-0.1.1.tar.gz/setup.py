# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane', 'arcane.ga4']

package_data = \
{'': ['*']}

install_requires = \
['arcane-core==1.7.0',
 'arcane-credentials==0.1.0',
 'arcane-datastore==1.1.0',
 'arcane-requests==0.3.0',
 'google-analytics-admin==0.8.1',
 'google-api-core==1.31.5',
 'google-auth>=1.30.0,<2.0.0']

setup_kwargs = {
    'name': 'arcane-ga4',
    'version': '0.1.1',
    'description': 'Utility functions for ga4 api call',
    'long_description': '# Arcane ga4 README\n\nThis package helps us to interact with Google Analytics V4 API:\n\n    + [Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)\n    + [Google Analytics Admin API](https://developers.google.com/analytics/devguides/config/admin/v1)\n\n\n## Release history\nTo see changes, please see CHANGELOG.md\n',
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
