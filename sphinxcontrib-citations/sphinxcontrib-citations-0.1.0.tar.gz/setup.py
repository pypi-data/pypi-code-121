# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['sphinxcontrib', 'sphinxcontrib.citations']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx>=4.0,<5.0', 'requests>=2.0,<3.0', 'sphinxcontrib-bibtex>=2.0,<3.0']

setup_kwargs = {
    'name': 'sphinxcontrib-citations',
    'version': '0.1.0',
    'description': 'Create a list with all the papers that cite yours',
    'long_description': None,
    'author': 'Gabriele Bozzola',
    'author_email': 'sbozzolator@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
