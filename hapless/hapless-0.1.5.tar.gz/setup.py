# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hapless']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.2,<9.0.0',
 'humanize>=4.0.0,<5.0.0',
 'psutil>=5.9.0,<6.0.0',
 'rich>=12.2.0,<13.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.11.3,<5.0.0']}

entry_points = \
{'console_scripts': ['hap = hapless.cli:cli']}

setup_kwargs = {
    'name': 'hapless',
    'version': '0.1.5',
    'description': 'Run and track processes in background',
    'long_description': '## hapless\n\n![Checks](https://github.com/bmwant/hapless/actions/workflows/tests.yml/badge.svg)\n[![PyPI](https://img.shields.io/pypi/v/hapless)](https://pypi.org/project/hapless/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hapless)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n> **hapless** (*adjective*) - (especially of a person) unfortunate. A developer who accidentally launched long-running process in the foreground.\n\nSimplest way of running and tracking processes in the background.\n\n[![asciicast](https://asciinema.org/a/489924.svg)](https://asciinema.org/a/489924?speed=2)\n\n### Installation\n\n```bash\n$ pip install hapless\n\n# or to make sure proper pip is used for the given python executable\n$ python -m pip install hapless\n```\n\nInstall into user-specific directory in case of any permissions-related issues.\n\n```bash\n$ pip install --user hapless\n$ python -m pip install --user hapless\n```\n\n### Usage\n\n```bash\n# Run arbitrary script\n$ hap run -- python long_running.py\n\n# Show summary table\n$ hap\n\n# Display status of the specific process\n$ hap status 1\n```\n\nSee [USAGE.md](https://github.com/bmwant/hapless/blob/main/USAGE.md) for the complete list of commands and available parameters.\n\n### Contribute\n\nSee [DEVELOP.md](https://github.com/bmwant/hapless/blob/main/DEVELOP.md) to setup your local development environment and feel free to create a pull request with a new feature.\n\n### Releases\n\nSee [CHANGELOG.md](https://github.com/bmwant/hapless/blob/main/CHANGELOG.md) for the new features included within each release.\n\n### See also\n\n* [Rich](https://rich.readthedocs.io/en/stable/introduction.html) console UI library.\n* [Supervisor](http://supervisord.org/) full-fledged process manager.\n* [podmena](https://github.com/bmwant/podmena) provides nice emoji icons to commit messages.\n\n### Support project, support 🇺🇦 Ukraine!\n\n🐶 `D7DA74qzZUyh9cctCxWovPTEovUSjGzL2S` this is [Dogecoin](https://dogecoin.com/) wallet to support the project.\n\n🇺🇦 All donations will go towards supporting Ukraine in the war.\n\n✉️ [Contact author](mailto:bmwant@gmail.com) directly in case you want to donate with some different payment option or check what has already been done.\n',
    'author': 'Misha Behersky',
    'author_email': 'bmwant@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bmwant/hapless',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
