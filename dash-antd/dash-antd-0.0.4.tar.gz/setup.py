# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dash_antd']

package_data = \
{'': ['*']}

install_requires = \
['dash>=2.4,<3.0']

setup_kwargs = {
    'name': 'dash-antd',
    'version': '0.0.4',
    'description': 'Ant Design components for Plotly Dash',
    'long_description': None,
    'author': 'Robert Pack',
    'author_email': 'robstar.pack@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
