# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['syringe_pumps', 'syringe_pumps.camera_control', 'syringe_pumps.pump_control']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'syringe-pumps',
    'version': '0.1.3',
    'description': 'Library for the control of syringe pumps',
    'long_description': None,
    'author': 'Diana Arguijo',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
