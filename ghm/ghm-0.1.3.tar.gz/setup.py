# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ghm']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0', 'pygit2>=1.9,<2.0']

entry_points = \
{'console_scripts': ['ghm = ghm.cli:main']}

setup_kwargs = {
    'name': 'ghm',
    'version': '0.1.3',
    'description': 'GitHub Mirrorer - Bulk mirror GitHub repositories',
    'long_description': '# Github Mirrorer\n\n[![Continuous Integration](https://github.com/mconigliaro/ghm/actions/workflows/ci.yml/badge.svg)](https://github.com/mconigliaro/ghm/actions/workflows/ci.yml)\n\nSimple command-line utility for bulk mirroring GitHub repositories\n\n## Installation\n\n    pip install ghm\n\n## Running the Application\n\n    ghm [options] <path>\n\nUse `--help` to see available options.\n\n## Development\n\n### Getting Started\n\n    poetry install\n    poetry shell\n    ...\n\n### Running Tests\n\n    pytest\n\n### Releases\n\n1. Bump `version` in [pyproject.toml](pyproject.toml)\n1. Update [CHANGELOG.md](CHANGELOG.md)\n1. Run `make release`\n',
    'author': 'Mike Conigliaro',
    'author_email': 'mike@conigliaro.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mconigliaro/ghm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
