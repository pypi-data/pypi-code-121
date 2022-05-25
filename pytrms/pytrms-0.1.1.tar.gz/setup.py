# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytrms']

package_data = \
{'': ['*']}

install_requires = \
['h5py>=3.6.0,<4.0.0']

setup_kwargs = {
    'name': 'pytrms',
    'version': '0.1.1',
    'description': 'Python bundle for proton-transfer reaction mass-spectrometry (PTR-MS).',
    'long_description': None,
    'author': 'Moritz Koenemann',
    'author_email': 'github@lefitz.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
