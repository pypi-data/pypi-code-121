# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypandora']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

extras_require = \
{'docs': ['Sphinx>=4.5,<5.0']}

entry_points = \
{'console_scripts': ['pandora = pypandora:main']}

setup_kwargs = {
    'name': 'pypandora',
    'version': '0.8',
    'description': 'Python CLI and module for pandora',
    'long_description': '# Python client and module for Pandora\n\n## Installation\n\n```bash\npip install pypandora\n```\n\n## Usage\n\n### Command line\n\nYou can use the `pandora` command to submit a file:\n\n```bash\n$ pandora -h\nusage: pandora [-h] [--url URL] (--redis_up | -f FILE)\n\nSubmit a file.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --url URL             URL of the instance (defaults to https://pandora.circl.lu/).\n  --redis_up            Check if redis is up.\n  -f FILE, --file FILE  Path to the file to submit.\n\n```\n\n### Library\n\nSee [API Reference](https://pypandora.readthedocs.io/en/latest/api_reference.html)\n',
    'author': 'Raphaël Vinot',
    'author_email': 'raphael.vinot@circl.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pandora-analysis/pypandora',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
