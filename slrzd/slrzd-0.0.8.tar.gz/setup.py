# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slrzd']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.11.2,<3.0.0']

setup_kwargs = {
    'name': 'slrzd',
    'version': '0.0.8',
    'description': 'Solarize everything',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'angelo@ragt.ag',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
