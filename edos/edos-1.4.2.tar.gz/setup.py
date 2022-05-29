# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edos',
 'edos.api',
 'edos.api.digitalocean',
 'edos.api.digitalocean.databases',
 'edos.api.digitalocean.databases.models',
 'edos.api.swarmpit',
 'edos.api.swarmpit.models',
 'edos.cli',
 'edos.cli.do',
 'edos.services',
 'edos.settings']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'appdirs>=1.4.4,<2.0.0',
 'boto3>=1.23.10,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'diskcache>=5.4.0,<6.0.0',
 'docker>=5.0.3,<6.0.0',
 'paramiko>=2.11.0,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'tabulate>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['edos = edos.main:main',
                     'edos-configure = edos.config:configure_interactive']}

setup_kwargs = {
    'name': 'edos',
    'version': '1.4.2',
    'description': 'Internal tool for managing docker swarm cluster and DO services',
    'long_description': None,
    'author': 'Štěpán Binko',
    'author_email': 'stepanjr@binko.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
