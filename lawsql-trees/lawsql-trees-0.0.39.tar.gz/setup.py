# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lawsql_trees']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3.7,<4.0.0',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'citation-decision>=0.0.6,<0.0.7',
 'html5lib>=1.1,<2.0',
 'python-slugify>=6.1.2,<7.0.0',
 'sqlite-utils>=3.26,<4.0',
 'statute-matcher>=0.0.3,<0.0.4',
 'treeish>=0.0.2,<0.0.3']

setup_kwargs = {
    'name': 'lawsql-trees',
    'version': '0.0.39',
    'description': 'Pull and format statute / codification data (tree structures) from local path to raw yaml files.',
    'long_description': 'None',
    'author': 'Marcelino G. Veloso III',
    'author_email': 'mars@veloso.one',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
