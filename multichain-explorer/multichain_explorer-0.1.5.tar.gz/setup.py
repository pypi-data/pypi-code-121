# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multichain_explorer',
 'multichain_explorer.src',
 'multichain_explorer.src.models',
 'multichain_explorer.src.models.provider_models',
 'multichain_explorer.src.providers',
 'multichain_explorer.src.providers.ada',
 'multichain_explorer.src.providers.algo',
 'multichain_explorer.src.providers.btc',
 'multichain_explorer.src.providers.eth',
 'multichain_explorer.src.providers.luna',
 'multichain_explorer.src.services',
 'multichain_explorer.src.validators',
 'multichain_explorer.src.validators.ada',
 'multichain_explorer.src.validators.algo',
 'multichain_explorer.src.validators.btc',
 'multichain_explorer.src.validators.eth',
 'multichain_explorer.src.validators.luna']

package_data = \
{'': ['*']}

install_requires = \
['blockfrost-python>=0.4.3,<0.5.0',
 'cryptos>=1.36,<2.0',
 'py-algorand-sdk>=1.11.0,<2.0.0',
 'terra-sdk>=2.0.5,<3.0.0',
 'web3>=5.28,<6.0']

entry_points = \
{'console_scripts': ['my-project = multichain_explorer.main:run']}

setup_kwargs = {
    'name': 'multichain-explorer',
    'version': '0.1.5',
    'description': 'A simple package to explore multiple blockchains in an homogeneous way',
    'long_description': None,
    'author': 'sdominguez894',
    'author_email': 'sdominguez894@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
