# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyslac', 'pyslac.examples', 'pyslac.sockets']

package_data = \
{'': ['*']}

install_requires = \
['environs>=9.5.0,<10.0.0']

setup_kwargs = {
    'name': 'pyslac',
    'version': '0.8.1',
    'description': 'SLAC Protocol implementation, defined in ISO15118-3',
    'long_description': None,
    'author': 'André Duarte',
    'author_email': 'andre@switch-ev.com, andre14x@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
