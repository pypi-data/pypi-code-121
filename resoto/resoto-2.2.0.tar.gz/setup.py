# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['resoto']

package_data = \
{'': ['*']}

install_requires = \
['resoto-plugins==2.2.0',
 'resotocore==2.2.0',
 'resotometrics==2.2.0',
 'resotoshell==2.2.0',
 'resotoworker==2.2.0']

setup_kwargs = {
    'name': 'resoto',
    'version': '2.2.0',
    'description': 'Resoto bundle - single package for resoto components',
    'long_description': 'Meta package containing all resoto components.\n\nInstallation:\n\n```\npip install resoto\n```',
    'author': 'Some Engineering Inc.',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/someengineering/resoto',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
