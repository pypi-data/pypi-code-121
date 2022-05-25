# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lifeomic_chatbot_tools',
 'lifeomic_chatbot_tools.aws',
 'lifeomic_chatbot_tools.ml',
 'lifeomic_chatbot_tools.persistence',
 'lifeomic_chatbot_tools.persistence.record_store',
 'lifeomic_chatbot_tools.types',
 'lifeomic_chatbot_tools.types.conversations',
 'lifeomic_chatbot_tools.web']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.63.0,<1.0.0',
 'loguru>=0.5.1,<1.0.0',
 'pydantic>=1.7.3,<1.9.0',
 'requests>=2.21.0,<3.0.0']

extras_require = \
{'aws': ['boto3>=1.21.7,<2.0.0'],
 'ml': ['numpy>=1.19.2,<2.0.0',
        'scikit-learn>=0.24.2,<2.0.0',
        'networkx>=2.5.1,<3.0.0']}

setup_kwargs = {
    'name': 'lifeomic-chatbot-tools',
    'version': '5.0.0',
    'description': 'Utilities for machine learning, web services, and cloud infrastructure.',
    'long_description': '# lifeomic-chatbot-tools\n\nPython utilities for machine learning, web services, and cloud infrastructure.\nIncludes classes and methods for:\n\n1. ML model serialization/deserialization\n2. ML model evaluation utilities\n3. Data structures/models related to chatbots\n4. ML model artifact persistence and version management\n5. And more\n\nThe data structures in this package can all be found in the\n`lifeomic_chatbot_tools.types` sub-package, and are all\n[Pydantic](https://pydantic-docs.helpmanual.io/) data models. For example the\n`lifeomic_chatbot_tools.types.agent.AgentConfig` class represents a chatbot\'s\nconfiguration and training data.\n\n## Getting Started\n\nTo begin using the package, use your favorite package manager to install it from PyPi.\nFor example, using pip:\n\n```\npip install lifeomic-chatbot-tools\n```\n\nSome of the features in this repo require more heavy weight dependencies, like AWS\nrelated utilities, or utilities specific to machine learning. If you try to import\nthose features, they will tell you if you do not have the correct package extra\ninstalled. For example, many of the features in the `lifeomic_chatbot_tools.ml`\nsub-package require the `ml` extra. To install `lifeomic-chatbot-tools` with that\nextra:\n\n```\npip install lifeomic-chatbot-tools[ml]\n```\n\nYou can then begin using any package features that require ML dependencies.\n\n## Developing Locally\n\nBefore making any new commits or pull requests, please complete these steps.\n\n1. Install the Poetry package manager for Python if you do not already have it.\n   Installation instructions can be found\n   [here](https://python-poetry.org/docs/#installation).\n2. Clone the project.\n3. From the root directory of the repo, install the dependencies, including all dev\n   dependencies and extras:\n   ```\n   poetry install --extras "aws ml"\n   ```\n4. Install the pre-commit hooks, so they will run before each local commit. This\n   includes linting, auto-formatting, and import sorting:\n   ```\n   pre-commit install\n   ```\n   **Note**: pre-commit is a dev dependency of the project, and is managed by Poetry.\n   In order to use those dependencies from the terminal, you must be in a Poetry shell.\n   This can be accomplished by first running `poetry shell` in your terminal.\n\n## Testing Locally\n\nWith Yarn, Docker, and docker-compose installed, run this command from the project\nroot:\n\n```\nyarn ci-test\n```\n\nThis will build the project, lint it, and run the unit tests and integration tests.\nAll those steps can be run individually as well. See the scripts in the `package.json`\nfile for the command names.\n\n## Releasing The Package\n\nReleasing the package is automatically handled by CI, but three steps must be taken\nto trigger a successful release:\n\n1. Use Poetry\'s [`version` command](https://python-poetry.org/docs/cli/#version) to\n   bump the package\'s version.\n2. Commit and tag the repo with the exact same version the package was bumped to,\n   e.g. `v1.0.0` (include a preceding `v`).\n3. Push the commit and tag to remote. These can be done together using:\n   `git push --atomic origin <branch_name> <tag>`\n\nCI will then build release the package to pypi with that version once the commit and\ntag are merged to the `master` branch.\n',
    'author': 'LifeOmic Development',
    'author_email': 'development@lifeomic.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
