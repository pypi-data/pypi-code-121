# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['coveo_pypi_cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1',
 'coveo-settings>=2.0.0,<3.0.0',
 'coveo-styles>=2.0.0,<3.0.0',
 'coveo-systools>=2.0.0,<3.0.0',
 'requests',
 'typing-extensions']

entry_points = \
{'console_scripts': ['pypi = coveo_pypi_cli.cli:pypi']}

setup_kwargs = {
    'name': 'coveo-pypi-cli',
    'version': '2.1.2',
    'description': 'Query and compute pypi versions from command line.',
    'long_description': '# coveo-pypi-cli\n\nA very simple pypi cli that can be used to obtain the latest version of a package, or calculate the next one.\n\nServes our automatic pypi push github action.\n\n\n## `pypi current-version`\n\nDisplay the current version of a package from `pypi.org`\n\n\n## `pypi next-version`\n\nCompute the next version of a package.\n\n- Can be given a minimum version\n  - e.g.: pypi is `0.0.3` and mininum set to `0.1`: next version will be `0.1`\n- Supports computing pre-release versions\n\n# private index support\n\nYou can target a private pypi server through a switch or an environment variable.\n\n## Using the `--index` switch\n\n```shell\n$ pypi current-version secret-package --index https://my.pypi.server.org\n1.0.0\n\n$ pypi current-version secret-package --index https://my.pypi.server.org:51800/urlprefix\n1.0.0\n```\n\n## Using the environment variable:\n\n```shell\n$ PYPI_CLI_INDEX="https://my.pypi.server.org" pypi current-version secret-package\n```\n\nNote: Unlike `pip --index-url`, **you must omit** the `/simple` url prefix.\nThe API used by `coveo-pypi-cli` is served by the `/pypi` endpoint _and should not be specified either!_\n\n\n# pypi-cli in action\n\nThe best example comes from the [github action](../.github/workflows/actions/publish-to-pypi), which computes the next version based on the current release and what\'s in the `pyproject.toml`.\n\nHere\'s what you can expect from the tool:\n\n```shell\n$ pypi current-version coveo-functools\n0.2.1\n\n$ pypi next-version coveo-functools\n0.2.2\n\n$ pypi next-version coveo-functools --prerelease\n0.2.2a1\n\n$ pypi next-version coveo-functools --minimum-version 0.2\n0.2.2\n\n$ pypi next-version coveo-functools --minimum-version 0.3\n0.3\n\n$ pypi next-version coveo-functools --minimum-version 0.3 --prerelease\n0.3a1\n\n\n# Here\'s an example of how we use it in the github action\n\n$ poetry version\ncoveo-pypi-cli 0.1.0\n$ minimum_version=$(poetry version | cut --fields 2 --delimiter \' \' )\n0.1.0\n\n# when left unattended, the next-version increments the patch number\n$ pypi next-version coveo-pypi-cli --minimum-version $minimum_version\n0.2.2\n\n# in order to change the minor or major, because the script uses `poetry version` to obtain the minimum version, \n# just set it in `pyproject.toml` manually or by calling `poetry version <new-version>` (and commit!)\n$ poetry version 0.3\nBumping version from 0.1.0 to 0.3\n$ minimum_version=$(poetry version | cut --fields 2 --delimiter \' \' )\n0.3\n$ pypi next-version coveo-pypi-cli --minimum-version $minimum_version\n0.3\n\n# IMPORTANT: the publish step MUST set the computed version for poetry before publishing!\n$ poetry version $minimum_version\n0.3\n$ poetry publish\n...\n\n# after publishing the above, repeating the steps would yield:\n$ pypi next-version coveo-pypi-cli --minimum-version $minimum_version\n0.3.1\n\n# for completeness, you can also publish pre-releases:\n$ pypi next-version coveo-pypi-cli --minimum-version $minimum_version --prerelease\n0.3.1a1\n\n \n```\n',
    'author': 'Jonathan Piché',
    'author_email': 'tools@coveo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/coveooss/coveo-python-oss/tree/main/coveo-pypi-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
