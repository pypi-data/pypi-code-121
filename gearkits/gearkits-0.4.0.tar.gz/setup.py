# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gearkits']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.23.5,<2.0.0',
 'google-api-python-client>=2.48.0,<3.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'gearkits',
    'version': '0.4.0',
    'description': 'Gather all the general services api in basic usage. This package is built for what we need in our side projects of open source.',
    'long_description': '# GearKits\n\nGather all the general services API in basic usage. This package is built for what we need in our side projects of open source.\n\n    pip install gearkits\n\nor\n\n    poetry add gearkits\n\n## Services\n\n- telegram\n- gitlab\n- IPInfo\n',
    'author': 'Toomore Chiang',
    'author_email': 'toomore0929@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/toomore/gearkits',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
