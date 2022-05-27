# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hybrid_garden']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.4,<2.0.0',
 'pmlb>=1.0.1,<2.0.0',
 'pygad>=2.16.3,<3.0.0',
 'randomname>=0.1.5,<0.2.0',
 'scikit-learn>=1.1.1,<2.0.0']

setup_kwargs = {
    'name': 'hybrid-garden',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Ilona Kovaleva',
    'author_email': 'ilona.kovaleva.ds@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
