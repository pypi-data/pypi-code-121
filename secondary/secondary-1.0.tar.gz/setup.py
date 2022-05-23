# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['secondary']
setup_kwargs = {
    'name': 'secondary',
    'version': '1.0',
    'description': 'Printing your text(code) in slow mode & handwrite effect.',
    'long_description': None,
    'author': 'Flame',
    'author_email': 'matixsun1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
