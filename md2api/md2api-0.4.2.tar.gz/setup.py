# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['md2api']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.20,<4.0.0', 'markdown>=3.3.4,<4.0.0']

entry_points = \
{'console_scripts': ['md2api = md2api.run:main']}

setup_kwargs = {
    'name': 'md2api',
    'version': '0.4.2',
    'description': '',
    'long_description': None,
    'author': 'sumeshi',
    'author_email': 'sum3sh1@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
