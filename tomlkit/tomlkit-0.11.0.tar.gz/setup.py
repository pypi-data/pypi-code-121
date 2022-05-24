# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tomlkit']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tomlkit',
    'version': '0.11.0',
    'description': 'Style preserving TOML library',
    'long_description': '[github_release]: https://img.shields.io/github/release/sdispater/tomlkit.svg?logo=github&logoColor=white\n[pypi_version]: https://img.shields.io/pypi/v/tomlkit.svg?logo=python&logoColor=white\n[python_versions]: https://img.shields.io/pypi/pyversions/tomlkit.svg?logo=python&logoColor=white\n[github_license]: https://img.shields.io/github/license/sdispater/tomlkit.svg?logo=github&logoColor=white\n[github_action]: https://github.com/sdispater/tomlkit/actions/workflows/tests.yml/badge.svg\n\n[![GitHub Release][github_release]](https://github.com/sdispater/tomlkit/releases/)\n[![PyPI Version][pypi_version]](https://pypi.org/project/tomlkit/)\n[![Python Versions][python_versions]](https://pypi.org/project/tomlkit/)\n[![License][github_license]](https://github.com/sdispater/tomlkit/blob/master/LICENSE)\n<br>\n[![Tests][github_action]](https://github.com/sdispater/tomlkit/actions/workflows/tests.yml)\n\n# TOML Kit - Style-preserving TOML library for Python\n\nTOML Kit is a **1.0.0-compliant** [TOML](https://toml.io/) library.\n\nIt includes a parser that preserves all comments, indentations, whitespace and internal element ordering,\nand makes them accessible and editable via an intuitive API.\n\nYou can also create new TOML documents from scratch using the provided helpers.\n\nPart of the implementation has been adapted, improved and fixed from [Molten](https://github.com/LeopoldArkham/Molten).\n\n## Usage\n\nSee the [documentation](docs/quickstart.rst) for more information.\n\n## Installation\n\nIf you are using [Poetry](https://poetry.eustace.io),\nadd `tomlkit` to your `pyproject.toml` file by using:\n\n```bash\npoetry add tomlkit\n```\n\nIf not, you can use `pip`:\n\n```bash\npip install tomlkit\n```\n\n## Running tests\n\nPlease clone the repo with submodules with the following command\n`git clone --recurse-submodules https://github.com/sdispater/tomlkit.git`.\nWe need the submodule - `toml-test` for running the tests.\n\nYou can run the tests with `poetry run pytest -q tests`\n',
    'author': 'Sébastien Eustace',
    'author_email': 'sebastien@eustace.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sdispater/tomlkit',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
