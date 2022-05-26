# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tikka',
 'tikka.adapters',
 'tikka.adapters.network',
 'tikka.adapters.network.rpc',
 'tikka.adapters.repository',
 'tikka.domains',
 'tikka.domains.entities',
 'tikka.interfaces',
 'tikka.interfaces.adapters',
 'tikka.interfaces.adapters.network',
 'tikka.interfaces.adapters.repository',
 'tikka.interfaces.domains',
 'tikka.interfaces.entities',
 'tikka.libs',
 'tikka.slots',
 'tikka.slots.pyqt',
 'tikka.slots.pyqt.entities',
 'tikka.slots.pyqt.models',
 'tikka.slots.pyqt.resources',
 'tikka.slots.pyqt.resources.gui',
 'tikka.slots.pyqt.resources.gui.widgets',
 'tikka.slots.pyqt.resources.gui.windows',
 'tikka.slots.pyqt.resources.icons',
 'tikka.slots.pyqt.widgets',
 'tikka.slots.pyqt.windows']

package_data = \
{'': ['*'],
 'tikka': ['locales/en_US/*',
           'locales/en_US/LC_MESSAGES/*',
           'locales/fr_FR/*',
           'locales/fr_FR/LC_MESSAGES/*'],
 'tikka.adapters.repository': ['assets/*', 'assets/migrations/*']}

install_requires = \
['PyQt5>=5.15.6,<6.0.0',
 'PyYAML>=6.0,<7.0',
 'duniterpy==1.0.0',
 'mnemonic>=0.19,<0.20',
 'substrate-interface>=1.2.4,<2.0.0',
 'yoyo-migrations>=7.3.1,<8.0.0']

entry_points = \
{'console_scripts': ['tikka = tikka.__main__:main']}

setup_kwargs = {
    'name': 'tikka',
    'version': '0.5.4',
    'description': 'Tikka is a fast and light Python/Tk client to manage your Ğ1 accounts',
    'long_description': None,
    'author': 'Vincent Texier',
    'author_email': 'vit@free.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
