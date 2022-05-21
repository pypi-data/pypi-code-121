# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vigilant_crypto_snatch',
 'vigilant_crypto_snatch.commands',
 'vigilant_crypto_snatch.configuration',
 'vigilant_crypto_snatch.datastorage',
 'vigilant_crypto_snatch.evaluation',
 'vigilant_crypto_snatch.feargreed',
 'vigilant_crypto_snatch.historical',
 'vigilant_crypto_snatch.marketplace',
 'vigilant_crypto_snatch.notifications',
 'vigilant_crypto_snatch.qtgui',
 'vigilant_crypto_snatch.qtgui.control',
 'vigilant_crypto_snatch.qtgui.ui',
 'vigilant_crypto_snatch.reporting',
 'vigilant_crypto_snatch.triggers']

package_data = \
{'': ['*']}

install_requires = \
['BitstampClient>=2.2.8,<3.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'ccxt>=1.74.11,<2.0.0',
 'click>=8.0.0,<9.0.0',
 'coloredlogs>=15.0,<16.0',
 'krakenex>=2.1.0,<3.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'pyyaml>=6.0,<7.0',
 'requests>=2.25.1,<3.0.0',
 'sqlalchemy>=1.4.27,<2.0.0',
 'urllib3>=1.26.3,<2.0.0']

extras_require = \
{'evaluation': ['pandas>=1.3.4,<2.0.0',
                'scipy>=1.7.2,<2.0.0',
                'streamlit>=1.2.0,<2.0.0',
                'altair>=4.1.0,<5.0.0'],
 'gui': ['PyQt6>=6.3.0,<7.0.0']}

entry_points = \
{'console_scripts': ['vigilant-crypto-snatch = vigilant_crypto_snatch.cli:main',
                     'vigilant-crypto-snatch-qt = '
                     'vigilant_crypto_snatch.qtgui.__main__:main']}

setup_kwargs = {
    'name': 'vigilant-crypto-snatch',
    'version': '5.7.0b2',
    'description': 'Crypto currency buying agent',
    'long_description': None,
    'author': 'Martin Ueding',
    'author_email': 'mu@martin-ueding.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
