# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['smtptester']

package_data = \
{'': ['*'], 'smtptester': ['assets/*']}

install_requires = \
['dnspython>=2.2,<3.0', 'pyside6>=6.3,<7.0']

entry_points = \
{'console_scripts': ['smtptester = smtptester.cli:main',
                     'smtptester-gui = smtptester.gui:main']}

setup_kwargs = {
    'name': 'smtptester',
    'version': '1.1.1',
    'description': 'A graphical and command line SMTP diagnostic tool',
    'long_description': '# SMTP Tester\n\n[![Continuous Integration](https://github.com/mconigliaro/smtptester/actions/workflows/ci.yml/badge.svg)](https://github.com/mconigliaro/smtptester/actions/workflows/ci.yml)\n\nAs a consultant at a managed services provider, I spent a long time searching for a tool that would help me troubleshoot SMTP problems quickly and easily without having to resort to telnet. Finally, I gave up and wrote my own.\n\n![](https://raw.githubusercontent.com/mconigliaro/smtptester/master/screenshots/smtptester-gui.png)\n\n## Features\n\n- Command-line and [graphical](https://www.qt.io/qt-for-python) user interfaces\n- Ability to override all DNS and SMTP settings\n- Support for SMTP authentication and TLS encryption\n\n## Installation\n\n    pip install smtptester\n\n## Running the Application\n\n### With GUI\n\n    smtptester-gui [options]\n\n### CLI Only\n\n    smtptester <options>\n\n## Development\n\n### Getting Started\n\n    poetry install\n    poetry shell\n    ...\n\n### Running Tests\n\n    pytest\n\n### Releases\n\n1. Bump `version` in [pyproject.toml](pyproject.toml)\n1. Update [CHANGELOG.md](CHANGELOG.md)\n1. Run `make release`\n',
    'author': 'Mike Conigliaro',
    'author_email': 'mike@conigliaro.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mconigliaro/smtptester',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
