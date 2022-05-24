# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cat_merge', 'cat_merge.model']

package_data = \
{'': ['*']}

install_requires = \
['mkdocs>=1.3.0,<2.0.0', 'pandas>=1.4.2,<2.0.0']

entry_points = \
{'console_scripts': ['cat-merge = cat_merge.merge:merge']}

setup_kwargs = {
    'name': 'cat-merge',
    'version': '0.1.10',
    'description': '',
    'long_description': None,
    'author': 'Monarch Initiative',
    'author_email': 'info@monarchinitiative.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
