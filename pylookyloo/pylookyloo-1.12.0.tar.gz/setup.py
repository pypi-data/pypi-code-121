# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylookyloo']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

extras_require = \
{'docs': ['Sphinx>=4.5.0,<5.0.0']}

entry_points = \
{'console_scripts': ['lookyloo = pylookyloo:main']}

setup_kwargs = {
    'name': 'pylookyloo',
    'version': '1.12.0',
    'description': 'Python CLI and module for Lookyloo',
    'long_description': '[![Documentation Status](https://readthedocs.org/projects/pylookyloo/badge/?version=latest)](https://pylookyloo.readthedocs.io/en/latest/?badge=latest)\n\n# PyLookyloo\n\nThis is the client API for [Lookyloo](https://www.lookyloo.eu).\n\n## Installation\n\n```bash\npip install pylookyloo\n```\n\n## Usage\n\n### Command line\n\nYou can use the `lookyloo` command to enqueue a URL.\n\n```bash\nusage: lookyloo [-h] [--url URL] --query QUERY\n\nEnqueue a URL on Lookyloo.\n\noptional arguments:\n  -h, --help     show this help message and exit\n  --url URL      URL of the instance (defaults to https://lookyloo.circl.lu/,\n                 the public instance).\n  --query QUERY  URL to enqueue.\n  --listing      Should the report be publicly listed.\n  --redirects    Get redirects for a given capture.\n\nThe response is the permanent URL where you can see the result of the capture.\n```\n\n### Library\n\nSee [API Reference](https://pylookyloo.readthedocs.io/en/latest/api_reference.html)\n',
    'author': 'Raphaël Vinot',
    'author_email': 'raphael.vinot@circl.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lookyloo/PyLookyloo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
