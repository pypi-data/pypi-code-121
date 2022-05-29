# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scuzzie']

package_data = \
{'': ['*']}

install_requires = \
['Mako>=1.2.0,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'marshmallow>=3.15.0,<4.0.0',
 'python-slugify>=6.1.2,<7.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['scuzzie = scuzzie.cli:scuzzie']}

setup_kwargs = {
    'name': 'scuzzie',
    'version': '0.2.0',
    'description': 'a simple webcomic static site generator',
    'long_description': '# scuzzie\n\nsimple static webcomic site generator\n\n',
    'author': 'backwardspy',
    'author_email': 'backwardspy@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/backwardspy/scuzzie',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
