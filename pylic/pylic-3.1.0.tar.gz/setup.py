# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylic', 'pylic.cli', 'pylic.cli.commands']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4.11.3,<5.0.0', 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['pylic = pylic.cli.app:main']}

setup_kwargs = {
    'name': 'pylic',
    'version': '3.1.0',
    'description': 'A Python license checker',
    'long_description': '# pylic - Python license checker [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/sandrochuber/pylic/blob/main/LICENSE) [![PyPI version](https://badge.fury.io/py/pylic.svg)](https://badge.fury.io/py/pylic/) [![Codecov](https://codecov.io/gh/ubersan/pylic//branch/main/graph/badge.svg)](https://codecov.io/gh/ubersan/pylic/)\n\nReads pylic configuration in `pyproject.toml` and checks licenses of installed packages recursively.\n\nPrinciples:\n- Every license has to be allowed explicitly (case-insensitive comparison).\n- All installed packages without a license are considered unsafe and have to be listed as such.\n\n> Only installed packages are checked for licenses. Packages/dependencies listed in `pyproject.toml` are ignored.\n\n## Installation\n\n```sh\npip install pylic\n```\n\n## Configuration\n\n`pylic` needs be run in the directory where your `pyproject.toml` file is located. You can configure\n- `safe_licenses`: All licenses you consider safe for usage. The string comparison is case-insensitive.\n- `unsafe_packages`: If you rely on a package that does not come with a license you have to explicitly list it as such.\n- `ignore_packages`: Packages that will not be reported as unsafe even if they use a license not listed as safe.\n\n```toml\n[tool.pylic]\nsafe_licenses = [\n    "Apache Software License",\n    "Apache License 2.0",\n    "MIT License",\n    "Python Software Foundation License",\n    "Mozilla Public License 2.0 (MPL 2.0)",\n]\nunsafe_packages = [\n    "unlicensedPackage",\n]\nignore_packages = [\n    "ignoredPackage",\n]\n```\n\n## Commands\n\n`pylic` provides the following commands (also see `pylic help`):\n- `check`: Checks all installed licenses.\n- `list`: Lists all installed packages and their corresponding license.\n\n## Usage Example\n\nCreate a venv to start with a clean ground and activate it\n\n```sh\npython -m venv .venv\nsource .venv/bin/activate\n```\n\nInstall `pylic` and create an empty `pyproject.toml`\n\n```sh\npip install pylic\ntouch pyproject.toml\n```\n\nInstall all your dependencies\n\n```sh\npip install <packageA> <packageB>\n```\n\nRun pylic\n\n```sh\npylic check\n```\n\nThe output will be similar to\n\n```sh\nFound unsafe packages:\n  pkg_resources (0.0.0)\nFound unsafe licenses:\n  pip (18.1): MIT License\n  zipp (3.4.1): MIT License\n  toml (0.10.2): MIT License\n  pylic (1.2.0): MIT License\n  setuptools (40.8.0): MIT License\n  typing-extensions (3.7.4.3): Python Software Foundation License\n  importlib-metadata (3.9.0): Apache Software License\n```\n\nThe return code of `pylic` is in this case non-zero due to unsafe licenses. This allows usage of pylic in CI.\n\n```sh\necho $? # prints 1\n```\n\nAs these licenses and packages are all ok we can configure `pylic` accordingly\n\n```sh\ncat <<EOT >> pyproject.toml\n[tool.pylic]\nsafe_licenses = ["Apache Software License", "MIT License", "Python Software Foundation License"]\nunsafe_packages = ["pkg_resources"]\nEOT\n```\n\nAfter rerunning `pylic check` the output now reveals a successful validation\n\n```sh\n✨ All licenses ok ✨\n```\n\nAlso the return code now signals that all is good\n\n```sh\necho $? # prints 0\n```\n\nUse `pylic list` to list all installed packages and their corresponding licenses.\n\n## Development\n\nRequired tools:\n- Poetry (https://python-poetry.org/)\n\nRun `poetry install` to install all necessary dependencies. Checkout the `[tool.taskipy.tasks]` (see [taskipy](https://github.com/illBeRoy/taskipy)) section in the `pyproject.toml` file for utility tasks. You can run these with `poetry run task <task>`.\n\nCreating a new release is as simple as:\n- Update `version` in the pyproject.toml and the `__version__.py` file.\n- `poetry run task release`.\n',
    'author': 'Sandro Huber',
    'author_email': 'sandrochuber@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ubersan/pylic',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
