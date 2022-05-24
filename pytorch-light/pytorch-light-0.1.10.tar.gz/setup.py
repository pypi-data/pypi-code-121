# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torchlight', 'torchlight.training', 'torchlight.utils']

package_data = \
{'': ['*']}

install_requires = \
['pycarton', 'pytorch-ignite', 'torch', 'transformers']

setup_kwargs = {
    'name': 'pytorch-light',
    'version': '0.1.10',
    'description': 'Light.',
    'long_description': None,
    'author': 'Yevgnen Koh',
    'author_email': 'wherejoystarts@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
