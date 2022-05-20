# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tapisservice',
 'tapisservice.tapisdjango',
 'tapisservice.tapisfastapi',
 'tapisservice.tapisflask']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodome>=3.6.0', 'tapipy>=1.1.1']

setup_kwargs = {
    'name': 'tapisservice',
    'version': '1.2.1',
    'description': "Python lib for interacting with an instance of the Tapis API Framework's tapisservice plugin.",
    'long_description': 'Tapipy plugin granting Tapis service functionality using `import tapisservice`.',
    'author': 'Joe Stubbs',
    'author_email': 'jstubbs@tacc.utexas.edu',
    'maintainer': 'Joe Stubbs',
    'maintainer_email': 'jstubbs@tacc.utexas.edu',
    'url': 'https://github.com/tapis-project/tapipy-tapisservice',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
