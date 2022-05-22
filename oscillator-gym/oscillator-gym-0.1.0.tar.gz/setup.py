# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oscillator']

package_data = \
{'': ['*']}

install_requires = \
['gym>=0.23.1,<0.24.0', 'numpy>=1.22.4,<2.0.0', 'pygame>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'oscillator-gym',
    'version': '0.1.0',
    'description': 'A simple harmonic oscillator gym environment',
    'long_description': None,
    'author': 'Onno Eberhard',
    'author_email': 'onnoeberhard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
