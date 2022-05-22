# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytorch_lightning_sam_callback']

package_data = \
{'': ['*']}

install_requires = \
['pytorch-lightning', 'torch']

setup_kwargs = {
    'name': 'pytorch-lightning-sam-callback',
    'version': '0.1.0',
    'description': '',
    'long_description': 'None',
    'author': 'Masahiro Wada',
    'author_email': 'argon.argon.argon@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
