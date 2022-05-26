# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rotary_states',
 'rotary_states.src',
 'rotary_states.src.integrators',
 'rotary_states.src.limit_cycles',
 'rotary_states.src.optimizers',
 'rotary_states.src.utils']

package_data = \
{'': ['*']}

install_requires = \
['numba>=0.55.0,<0.56.0', 'numpy>=1.18,<1.22', 'scipy>=1.7.3,<2.0.0']

setup_kwargs = {
    'name': 'rotary-states',
    'version': '0.1.1',
    'description': 'The minimalistic framework for finding rotational states',
    'long_description': None,
    'author': 'Dmitry Khorkin',
    'author_email': 'dmitryhorkin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
