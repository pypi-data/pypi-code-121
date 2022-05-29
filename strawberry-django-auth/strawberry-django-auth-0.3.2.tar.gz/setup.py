# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gqlauth',
 'gqlauth.administrator',
 'gqlauth.bases',
 'gqlauth.factory',
 'gqlauth.migrations',
 'gqlauth.user']

package_data = \
{'': ['*'], 'gqlauth': ['templates/email/*'], 'gqlauth.factory': ['fonts/*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0',
 'strawberry-django-jwt>=0.2.0,<0.3.0',
 'strawberry-graphql>=0.114.0,<0.115.0']

setup_kwargs = {
    'name': 'strawberry-django-auth',
    'version': '0.3.2',
    'description': 'Graphql authentication system with Strawberry for Django.',
    'long_description': None,
    'author': 'nir',
    'author_email': 'nrbnlulu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
