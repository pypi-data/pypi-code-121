# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['auto_uncertainties']

package_data = \
{'': ['*']}

install_requires = \
['jax==0.3.13', 'numpy==1.22.4', 'scipy>=1.8.1']

setup_kwargs = {
    'name': 'auto-uncertainties',
    'version': '0.3.2',
    'description': 'Linear Uncertainty Propagation with Auto-Differentiation',
    'long_description': None,
    'author': 'Varchas Gopalaswamy',
    'author_email': 'vgop@lle.rochester.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
