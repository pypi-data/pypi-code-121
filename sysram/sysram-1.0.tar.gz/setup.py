# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['sysram']
setup_kwargs = {
    'name': 'sysram',
    'version': '1.0',
    'description': 'System ram widget',
    'long_description': None,
    'author': 'Flame',
    'author_email': 'matixsun1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
