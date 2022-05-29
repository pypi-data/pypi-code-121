# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['semby', 'semby.cli', 'semby.core']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['semby = semby.cli:app']}

setup_kwargs = {
    'name': 'semby',
    'version': '1.0.5',
    'description': 'A simple stack based assembly like programming language',
    'long_description': '# semby\n\nA simple stack based assembly like programming language\n\n## Installation\n\n`pip install semby`\n\n## Usage\n\n`semby compile <file> && semby exec <file>` or `semby run <file>`\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vcokltfre/semby',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
