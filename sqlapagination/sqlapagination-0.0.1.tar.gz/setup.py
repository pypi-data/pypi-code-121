# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlapagination',
 'sqlapagination.paginators',
 'sqlapagination.paginators.join_based',
 'sqlapagination.paginators.keyset',
 'sqlapagination.paginators.keyset.inspection',
 'sqlapagination.paginators.keyset.inspection.performance',
 'sqlapagination.paginators.keyset.utils',
 'sqlapagination.paginators.limit_offset']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.0']

setup_kwargs = {
    'name': 'sqlapagination',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'GLEF1X',
    'author_email': 'glebgar567@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
