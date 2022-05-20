# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['minecraft_struct_building']

package_data = \
{'': ['*']}

install_requires = \
['mcpi>=1.2.1,<2.0.0', 'pandas>=1.4.1,<2.0.0']

entry_points = \
{'console_scripts': ['minecraft_struct_building = '
                     'minecraft_struct_building.minecraft_struct_building:main']}

setup_kwargs = {
    'name': 'minecraft-struct-building',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'konishi0125',
    'author_email': None,
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
