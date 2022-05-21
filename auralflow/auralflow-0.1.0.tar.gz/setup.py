# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['auralflow',
 'auralflow.datasets',
 'auralflow.losses',
 'auralflow.models',
 'auralflow.trainer',
 'auralflow.utils',
 'auralflow.visualizer']

package_data = \
{'': ['*']}

install_requires = \
['fast-bss-eval>=0.1.3,<0.2.0',
 'jupyter>=1.0.0,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'torch>=1.11.0,<2.0.0',
 'torchaudio>=0.11.0,<0.12.0']

setup_kwargs = {
    'name': 'auralflow',
    'version': '0.1.0',
    'description': 'A lightweight music source separation toolkit.',
    'long_description': None,
    'author': 'Kian Zohoury',
    'author_email': 'kzohoury@berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
