# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ec_slp_lib']
install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'ec-slp-lib',
    'version': '0.1.4',
    'description': 'Wrapper for Electron Cash commands based on its CLI and RPC commands',
    'long_description': None,
    'author': 'uak',
    'author_email': '4626956-uak@users.noreply.gitlab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/uak/electron-cash-slp-basic-lib',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
