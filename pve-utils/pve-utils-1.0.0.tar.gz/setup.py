# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pve_utils', 'pve_utils.commands', 'pve_utils.resources', 'pve_utils.utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'paramiko>=2.11.0,<3.0.0',
 'proxmoxer>=1.3.1,<2.0.0',
 'python-environ>=0.4.54,<0.5.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['create-lxc = pve_utils.commands:create_lxc',
                     'shell-lxc = pve_utils.commands:shell_lxc']}

setup_kwargs = {
    'name': 'pve-utils',
    'version': '1.0.0',
    'description': 'Utils to work with proxmox api',
    'long_description': '# PVE Utils\n## Commands\n  ```\n    - create-lxc\n    - shell-lxc\n  ```\n',
    'author': 'penkhasoveg',
    'author_email': 'pen.egor2002@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ghettoDdOS/pve-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
