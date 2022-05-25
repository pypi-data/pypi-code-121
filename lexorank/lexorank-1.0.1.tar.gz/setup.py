# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['lexorank']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'lexorank',
    'version': '1.0.1',
    'description': 'lexorank is a ranking system introduced by Atlassian JIRA.',
    'long_description': "# lexorank\n\nA reference implementation of a list ordering system like JIRA's Lexorank algorithm\n",
    'author': 'Gilles Wetzel',
    'author_email': 'gilles@wetzel.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wetgi/lexorank',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
