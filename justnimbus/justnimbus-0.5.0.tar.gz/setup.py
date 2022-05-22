# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['justnimbus']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'justnimbus',
    'version': '0.5.0',
    'description': 'A Python Wrapper for the Just Nimbus API',
    'long_description': None,
    'author': 'kvanzuijlen',
    'author_email': '8818390+kvanzuijlen@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
