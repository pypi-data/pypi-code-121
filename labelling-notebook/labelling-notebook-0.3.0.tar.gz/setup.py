# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['labelling', 'labelling.notebook']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['label = labelling.__main__:main']}

setup_kwargs = {
    'name': 'labelling-notebook',
    'version': '0.3.0',
    'description': 'An image annotation or labelling tool for small project',
    'long_description': None,
    'author': 'Wanasit ',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
