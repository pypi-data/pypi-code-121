# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nwon_baseline',
 'nwon_baseline.date_helper',
 'nwon_baseline.directory_helper',
 'nwon_baseline.file_helper',
 'nwon_baseline.image_helper',
 'nwon_baseline.import_helper',
 'nwon_baseline.poetry',
 'nwon_baseline.print_helper',
 'nwon_baseline.pydantic',
 'nwon_baseline.shell_helper',
 'nwon_baseline.type_helper',
 'nwon_baseline.typings']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2', 'pytz>=2022.1,<2023.0']

entry_points = \
{'console_scripts': ['prepare = scripts.prepare:prepare']}

setup_kwargs = {
    'name': 'nwon-baseline',
    'version': '0.1.29',
    'description': 'Python Code that is used in several projects',
    'long_description': '# NWON Python baseline package\n\nThis package provides some basic python functions that can be used across several projects.\n\nThe dependencies of the project are kept to a minimum in order to prevent version conflicts with other projects.\n\nPackage is meant for internal use at [NWON](https://nwon.de) as breaking changes may occur on version changes. This may change at some point but not for now 😇.\n\n## Development Setup\n\nWe recommend developing using poetry. \n\nThis are the steps to setup the project with a local virtual environment:\n\n1. Tell poetry to create dependencies in a `.venv` folder withing the project: `poetry config virtualenvs.in-project true`\n1. Create a virtual environment using the local python version: `poetry env use $(cat .python-version)`\n1. Install dependencies: `poetry install`\n\n## Prepare Package\n\nAs we want to include types with the package it is not as straight forward as just calling `poetry build` 😥.\n\nWe need to:\n\n1. Clean dist folder\n1. Bump up the version of the package\n1. Build the package\n\nLuckily we provide a script for doing all of this `python scripts/prepare.py patch`. Alternatively you can run the script in a poetry context `poetry run prepare patch`. The argument at the end defines whether you want a `patch`, `minor` or `major` version bump.\n\nThe final zipped data ends up in the `dist` folder.\n\n## Publish Package\n\nBefore publishing the package we need to:\n\n1. Add test PyPi repository: `poetry config repositories.testpypi https://test.pypi.org/legacy/`\n2. Publish the package to the test repository: `poetry publish -r testpypi`\n3. Test package: `pip install --index-url https://test.pypi.org/simple/ nwon_baseline`\n\nIf everything works fine publish the package via `poetry publish`.\n',
    'author': 'Reik Stiebeling',
    'author_email': 'reik.stiebeling@nwon.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://nwon.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
