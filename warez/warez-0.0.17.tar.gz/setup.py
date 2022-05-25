# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['warez', 'warez.pkg', 'warez.pkg.licensing', 'warez.src']

package_data = \
{'': ['*']}

install_requires = \
['pendulum>=2.1.2,<3.0.0', 'radon>=5.1.0,<6.0.0']

setup_kwargs = {
    'name': 'warez',
    'version': '0.0.17',
    'description': 'Decentralized software development',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'angelo@ragt.ag',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
