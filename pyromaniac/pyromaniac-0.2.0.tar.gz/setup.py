# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyromaniac']

package_data = \
{'': ['*']}

install_requires = \
['pyro-ppl>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'pyromaniac',
    'version': '0.2.0',
    'description': 'Helper modules for pyro.',
    'long_description': None,
    'author': 'Harald Vohringer',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
