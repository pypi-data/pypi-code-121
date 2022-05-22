# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['parrot_rcc']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.1.3,<9.0.0',
 'pyzeebe>=3.0.4,<4.0.0',
 'uvloop>=0.16.0,<0.17.0']

entry_points = \
{'console_scripts': ['parrot-rcc = parrot_rcc.cli:main']}

setup_kwargs = {
    'name': 'parrot-rcc',
    'version': '0.1.0',
    'description': 'Zeebe external task Robot Framework RCC client',
    'long_description': None,
    'author': 'Asko Soukka',
    'author_email': 'asko.soukka@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
