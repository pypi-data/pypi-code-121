# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyadb_gui']

package_data = \
{'': ['*']}

install_requires = \
['rich>=12.0.0,<13.0.0']

entry_points = \
{'console_scripts': ['pyadb = pyadb_gui.main:main']}

setup_kwargs = {
    'name': 'pyadb-gui',
    'version': '1.2.0',
    'description': 'Operate Android devices with a GUI tool producted by Python.',
    'long_description': None,
    'author': 'xq',
    'author_email': 'xq_work@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
