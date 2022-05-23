# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oscillator']

package_data = \
{'': ['*']}

install_requires = \
['gym>=0.22,<1.0', 'numpy', 'pygame']

setup_kwargs = {
    'name': 'oscillator-gym',
    'version': '1.0.2',
    'description': 'A simple harmonic oscillator environment for OpenAI Gym',
    'long_description': None,
    'author': 'Onno Eberhard',
    'author_email': 'onnoeberhard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
