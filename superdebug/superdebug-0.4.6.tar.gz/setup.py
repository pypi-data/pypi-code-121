# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['superdebug']

package_data = \
{'': ['*']}

install_requires = \
['mypyc-ipython>=0.0.2,<0.0.3', 'numpy>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'superdebug',
    'version': '0.4.6',
    'description': 'Convenient debugging for machine learning projects',
    'long_description': None,
    'author': 'Azure-Vision',
    'author_email': 'hewanrong2001@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
