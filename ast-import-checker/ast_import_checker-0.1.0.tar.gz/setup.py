# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ast_import_checker',
 'ast_import_checker.import_test_5',
 'ast_import_checker.import_test_6']

package_data = \
{'': ['*']}

install_requires = \
['absolutely_nothing>=0.1,<0.2', 'pytest>=6.0,<7.0']

entry_points = \
{'console_scripts': ['import_checker = import_checker.import_checker:main']}

setup_kwargs = {
    'name': 'ast-import-checker',
    'version': '0.1.0',
    'description': 'A small utility for checking python imports via the AST module',
    'long_description': None,
    'author': 'Zach Taira',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10.0,<4.0.0',
}


setup(**setup_kwargs)
