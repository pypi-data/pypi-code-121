# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qctrltoolkit', 'qctrltoolkit.superconducting', 'qctrltoolkit.utils']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.5,<2.0.0',
 'python-forge>=18.6.0,<19.0.0',
 'qctrl-commons>=16.0.0,<17.0.0',
 'scipy>=1.7.3,<2.0.0',
 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'qctrl-toolkit',
    'version': '0.1.0',
    'description': 'Q-CTRL Python Toolkit',
    'long_description': '# Q-CTRL Python Toolkit\n\nToolkit of convenience functions and classes for the Q-CTRL Python package.\n',
    'author': 'Q-CTRL',
    'author_email': 'support@q-ctrl.com',
    'maintainer': 'Q-CTRL',
    'maintainer_email': 'support@q-ctrl.com',
    'url': 'https://q-ctrl.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
