# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vidhash']

package_data = \
{'': ['*']}

install_requires = \
['ImageHash>=4.2.1,<5.0.0',
 'Pillow>=9.1.1,<10.0.0',
 'ffmpy3>=0.2.4,<0.3.0',
 'numpy>=1.22.4,<2.0.0']

setup_kwargs = {
    'name': 'vidhash',
    'version': '0.1.0',
    'description': 'A package for hashing videos and checking for similarity',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
