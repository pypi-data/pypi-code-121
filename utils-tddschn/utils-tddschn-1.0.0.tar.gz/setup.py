# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['utils_tddschn', 'utils_tddschn.sync']

package_data = \
{'': ['*']}

install_requires = \
['ipykernel>=6.13.0,<7.0.0', 'ipython>=8.3.0,<9.0.0']

setup_kwargs = {
    'name': 'utils-tddschn',
    'version': '1.0.0',
    'description': '',
    'long_description': '',
    'author': 'Xinyuan Chen',
    'author_email': '45612704+tddschn@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tddschn/utils-tddschn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
