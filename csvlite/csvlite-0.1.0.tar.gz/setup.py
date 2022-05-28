# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['csvlite']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['csvlite = csvlite.__main__:main']}

setup_kwargs = {
    'name': 'csvlite',
    'version': '0.1.0',
    'description': 'CSVLite',
    'long_description': '# CSVLite\n',
    'author': 'Luke Miloszewski',
    'author_email': 'lukemiloszewski@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lukemiloszewski/csvlite',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<3.10.0',
}


setup(**setup_kwargs)
