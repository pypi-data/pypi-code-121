# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shmtorch']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.4,<2.0.0', 'torch>=1.11.0,<2.0.0']

setup_kwargs = {
    'name': 'shmtorch',
    'version': '0.1.0',
    'description': 'shmtorch is an extension for PyTorch, which allows sharing DNN model weight tensors via Shared Memory.',
    'long_description': None,
    'author': 'freckie',
    'author_email': 'freckie@frec.kr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
