# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['databutton',
 'databutton.auth',
 'databutton.dataframes',
 'databutton.decorators',
 'databutton.helpers',
 'databutton.kubernetes',
 'databutton.server',
 'databutton.utils']

package_data = \
{'': ['*'], 'databutton': ['docker/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=7.0,<8.1',
 'databutton-web>=0.6.1,<0.7.0',
 'dataclasses-json>=0.5.7,<0.6.0',
 'fastapi>=0.78.0,<0.79.0',
 'httpx>=0.22.0,<0.23.0',
 'pandas>=0.21.0',
 'schedule>=1.1.0,<2.0.0',
 'sentry-sdk>=1.5.12,<2.0.0',
 'streamlit>=1.9.0,<2.0.0',
 'uvicorn>=0.17.6,<0.18.0',
 'watchgod>=0.8.2,<0.9.0',
 'websockets>=10.3,<11.0',
 'yaspin>=2.1.0,<3.0.0']

entry_points = \
{'console_scripts': ['databutton = databutton.cli:cli']}

setup_kwargs = {
    'name': 'databutton',
    'version': '0.9.0',
    'description': 'The CLI for databutton.com',
    'long_description': "# databutton-cli\n[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)\n[![PyPI version fury.io](https://badge.fury.io/py/databutton.svg)](https://pypi.python.org/pypi/databutton/)\n[![PyPI download week](https://img.shields.io/pypi/dw/databutton.svg)](https://pypi.python.org/pypi/databutton/)\n![release](https://github.com/databutton/databutton-cli/actions/workflows/release.yaml/badge.svg)\n\n\n\n\nThe CLI for building and deploying databutton projects\n\n## Getting Started\n\n`pip install databutton`\n\n`databutton create my-project`\n\n`databutton login`\n\n`databutton deploy`\n\n## Developing\n\n### Prerequisites\nThis project uses poetry, so if you haven't already;\n\n`pip install poetry`\n\n### Install dependencies\n\n`poetry install`\n\n### Test\n\n`poetry run pytest`\n\nAlternatively run `poetry run pytest -s` to see `print` statements for debugging purposes.\n\n### Test locally in another package\n\nTo test in another package, you can simply\n\n`pip install -e .` assuming you're in this folder. If not, replace the `.` with the path to the `databutton-cli` folder.\n\n## Authors\n\n* **Databutton** - *Initial work* - [github](https://github.com/databutton)\n\n## License: Copyright (c) Databutton\n\nAll rights reserved.",
    'author': 'Databutton',
    'author_email': 'hi@databutton.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
