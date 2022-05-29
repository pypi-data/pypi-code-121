# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cao_cli']

package_data = \
{'': ['*']}

install_requires = \
['pyperclip>=1.8.2,<2.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'typer>=0.4.1,<0.5.0',
 'wcwidth>=0.2.5,<0.3.0']

entry_points = \
{'console_scripts': ['cao = cao_cli.main:app', 'cao_test = cao_cli.main:app']}

setup_kwargs = {
    'name': 'cao-cli',
    'version': '1.0.1',
    'description': '',
    'long_description': '# cao-cli\n\n曹操命令行工具',
    'author': 'chenwei.hander',
    'author_email': 'chenwei.hander@bytedance.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
