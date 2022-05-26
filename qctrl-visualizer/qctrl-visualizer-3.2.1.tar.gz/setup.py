# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qctrlvisualizer']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=2.1', 'numpy>=1.21.5,<2.0.0', 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'qctrl-visualizer',
    'version': '3.2.1',
    'description': 'Q-CTRL Python Visualizer',
    'long_description': '# Q-CTRL Visualizer\n\nProvides visualization of data for Q-CTRL’s Python products.\n',
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
