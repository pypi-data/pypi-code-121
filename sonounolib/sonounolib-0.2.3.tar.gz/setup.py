# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sonounolib']

package_data = \
{'': ['*']}

install_requires = \
['SoundFile>=0.10.3,<0.11.0',
 'numpy>=1.22.4,<2.0.0',
 'sounddevice>=0.4.4,<0.5.0',
 'streamunolib>=0.4.3,<0.5.0']

setup_kwargs = {
    'name': 'sonounolib',
    'version': '0.2.3',
    'description': 'Library of generic sonification components.',
    'long_description': None,
    'author': 'Pierre Chanial',
    'author_email': 'pierre.chanial@apc.in2p3.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
