# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vsapy']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0',
 'gmpy2>=2.1.2,<3.0.0',
 'nltk>=3.7,<4.0',
 'numpy>=1.22.4,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'regex>=2022.4.24,<2023.0.0',
 'scipy>=1.8.1,<2.0.0',
 'setuptools>=62.3.2,<63.0.0',
 'six>=1.16.0,<2.0.0',
 'unicodedata2>=14.0.0,<15.0.0',
 'wheel>=0.37.1,<0.38.0',
 'xmltodict>=0.13.0,<0.14.0']

setup_kwargs = {
    'name': 'vsapy',
    'version': '0.6.0',
    'description': 'Vector Symbolic Architecture(VSA) library that allows building VSA apps that use various flavours of VSA vectors.',
    'long_description': None,
    'author': 'Chris Simpkin',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vsapy/vsapy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
