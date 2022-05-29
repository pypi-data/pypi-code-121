# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['veet',
 'veet.cli',
 'veet.commands',
 'veet.core',
 'veet.framework',
 'veet.framework.commands',
 'veet.framework.routing',
 'veet.framework.server']

package_data = \
{'': ['*']}

install_requires = \
['fnc>=0.5.3,<0.6.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.27.1,<3.0.0',
 'toml>=0.10.2,<0.11.0',
 'typer[all]>=0.4.1,<0.5.0']

extras_require = \
{':extra == "framework"': ['fastapi[all]>=0.78.0,<0.79.0']}

entry_points = \
{'console_scripts': ['veet = veet.cli:app']}

setup_kwargs = {
    'name': 'veet',
    'version': '0.1.0',
    'description': 'CLI for open source framework.',
    'long_description': '# Veet\nCLI for open source framework.\n\n## Installation\nInstallation is automated with the following command:\n\n```bash\n/bin/bash -c "$(curl -fsSL https://cli.veet.dev/install)"\n```\n',
    'author': 'Veet',
    'author_email': 'opensource@isamu.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://cli.veet.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
