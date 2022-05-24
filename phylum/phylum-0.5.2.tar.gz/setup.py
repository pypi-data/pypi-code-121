# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['phylum',
 'phylum.ci',
 'phylum.init',
 'tests',
 'tests.functional',
 'tests.unit']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=36.0.2,<37.0.0',
 'packaging>=21.3,<22.0',
 'requests>=2.27.1,<3.0.0',
 'ruamel.yaml>=0.17.21,<0.18.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.11.3,<5.0.0']}

entry_points = \
{'console_scripts': ['phylum-ci = phylum.ci.cli:script_main',
                     'phylum-init = phylum.init.cli:main']}

setup_kwargs = {
    'name': 'phylum',
    'version': '0.5.2',
    'description': 'Utilities for handling Phylum integrations',
    'long_description': '# phylum-ci\n[![PyPI](https://img.shields.io/pypi/v/phylum)](https://pypi.org/project/phylum/)\n![PyPI - Status](https://img.shields.io/pypi/status/phylum)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/phylum)](https://pypi.org/project/phylum/)\n[![GitHub](https://img.shields.io/github/license/phylum-dev/phylum-ci)](https://github.com/phylum-dev/phylum-ci/blob/main/LICENSE)\n[![GitHub issues](https://img.shields.io/github/issues/phylum-dev/phylum-ci)](https://github.com/phylum-dev/phylum-ci/issues)\n![GitHub last commit](https://img.shields.io/github/last-commit/phylum-dev/phylum-ci)\n[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/phylum-dev/phylum-ci/Test/main?label=Test&logo=GitHub)](https://github.com/phylum-dev/phylum-ci/actions/workflows/test.yml)\n\nPython package for handling CI and other integrations\n\n## Installation and usage\n\n### Installation\n\nThe `phylum` Python package is pip installable for the environment of your choice:\n\n```sh\npip install phylum\n```\n\nIt can also also be installed in an isolated environment with the excellent [`pipx` tool](https://pypa.github.io/pipx/):\n\n```sh\n# Globally install the app(s) on your system in an isolated virtual environment for the package\npipx install phylum\n\n# Use the apps from the package in an ephemeral environment\npipx run --spec phylum phylum-init <options>\npipx run --spec phylum phylum-ci <options>\n```\n\nThese installation methods require Python 3.7+ to run. For a self contained environment, consider using the Docker\nimage as described below.\n\n### Usage\n\nThe `phylum` Python package exposes its functionality with a command line interface (CLI).\nTo view the options available from the CLI, print the help message from one of the scripts provided as entry points:\n\n```sh\nphylum-init -h\nphylum-ci -h\n```\n\nThe functionality can also be accessed by calling the module:\n\n```sh\npython -m phylum.init -h\npython -m phylum.ci -h\n```\n\nThe functionality is also exposed in the form of a Docker image:\n\n```sh\n# Get the `latest` tagged image\ndocker pull phylumio/phylum-ci\n\n# View the help\ndocker run --rm phylumio/phylum-ci phylum-ci --help\n\n# Export a Phylum token (e.g., from `phylum auth token`)\nexport PHYLUM_API_KEY=$(phylum auth token)\n\n# Run it from a git repo directory containing a `.phylum_project` and a lockfile\ndocker run -it --rm -e PHYLUM_API_KEY --mount type=bind,src=$(pwd),dst=/phylum -w /phylum phylumio/phylum-ci\n```\n\nThe Docker image contains `git` and the installed `phylum` Python package.\nIt also contains an installed version of the Phylum CLI. The version of the Phylum CLI is the `latest` at the time of\nthe Docker image creation. An advantage of using the Docker image is that the complete environment is packaged and made\navailable with components that are known to work together.\n\n#### `phylum-init` Script Entry Point\n\nThe `phylum-init` script can be used to fetch and install the Phylum CLI.\nIt will attempt to install the latest released version of the CLI but can be specified to fetch a specific version.\nIt will attempt to automatically determine the correct CLI release, based on the platform where the script is run, but\na specific release target can be specified.\nIt will accept a Phylum token from an environment variable or specified as an option, but will also function in the case\nthat no token is provided. This can be because there is already a token set that should continue to be used or because\nno token exists and one will need to be manually created or set, after the CLI is installed.\n\n#### `phylum-ci` Script Entry Point\n\nThe `phylum-ci` script is for analyzing lockfile changes.\nThe script can be used locally or from within a Continuous Integration (CI) environment.\nIt will attempt to detect the CI platform based on the environment from which it is run and act accordingly.\nThe current CI platforms/environments supported are:\n\n* GitLab CI\n  * See the [GitLab CI Integration documentation](docs/gitlab_ci.md) for more info\n\n* None (local use)\n  * This is the "fall-through" case used when no other environment is detected\n  * Can be useful to analyze lockfiles locally, prior to or after submitting a pull/merge request (PR/MR) to a CI system\n    * Establishing a successful submission prior to submitting a PR/MR to a CI system\n    * Troubleshooting after submitting a PR/MR to a CI system and getting unexpected results\n\n## License\n\nMIT - with complete text available in the [LICENSE](LICENSE) file.\n\n## Contributing\n\nSuggestions and help are welcome. Feel free to open an issue or otherwise contribute.\nMore information is available on the [contributing documentation](CONTRIBUTING.md) page.\n\n## Change log\n\nAll notable changes to this project are documented in the [CHANGELOG](CHANGELOG.md).\n\nThe format of the change log is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\nand this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\nThe entries in the changelog are primarily automatically generated through the use of\n[conventional commits](https://www.conventionalcommits.org) and the\n[Python Semantic Release](https://python-semantic-release.readthedocs.io/en/latest/index.html) tool.\nHowever, some entries may be manually edited, where it helps for clarity and understanding.\n',
    'author': 'Phylum, Inc.',
    'author_email': 'engineering@phylum.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://phylum.io/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
