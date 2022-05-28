# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['archon', 'archon.actor', 'archon.actor.commands', 'archon.controller']

package_data = \
{'': ['*'], 'archon': ['etc/*']}

install_requires = \
['astropy>=5.0,<6.0',
 'click-default-group>=1.2.2,<2.0.0',
 'numpy>=1.19.5,<2.0.0',
 'sdss-clu>=1.3.0,<2.0.0',
 'sdsstools>=0.4.13']

setup_kwargs = {
    'name': 'sdss-archon',
    'version': '0.6.1',
    'description': 'A library and actor to communicate with an STA Archon controller.',
    'long_description': '# archon\n\n![Versions](https://img.shields.io/badge/python->3.8-blue)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Documentation Status](https://readthedocs.org/projects/sdss-archon/badge/?version=latest)](https://sdss-archon.readthedocs.io/en/latest/?badge=latest)\n[![Test](https://github.com/sdss/archon/actions/workflows/test.yml/badge.svg)](https://github.com/sdss/archon/actions/workflows/test.yml)\n[![Docker](https://github.com/sdss/archon/actions/workflows/docker.yml/badge.svg)](https://github.com/sdss/archon/actions/workflows/docker.yml)\n[![codecov](https://codecov.io/gh/sdss/archon/branch/main/graph/badge.svg)](https://codecov.io/gh/sdss/archon)\n\n\nA library and actor to communicate with an STA Archon controller.\n\n## Installation\n\nIn general you should be able to install ``archon`` by doing\n\n```console\npip install sdss-archon\n```\n\nTo build from source, use\n\n```console\ngit clone git@github.com:sdss/archon\ncd archon\npip install .\n```\n\n## Docker\n\nThe actor can run as a Docker container; new images for ``main`` (pointing to tag ``latest``) and tags are created via a GitHub Action. The images are stored in the GitHub Container Registry. To pull the latest image run\n\n```console\ndocker pull ghcr.io/sdss/archon:latest\n```\n\nTo run a container\n\n```console\ndocker run --name archon --rm --detach --network host ghcr.io/sdss/archon:latest\n```\n\nThis assumes that RabbitMQ is running on the default port in the host computer and that the Archon controllers are accessible over the host network.\n\n## Development\n\n`archon` uses [poetry](http://poetry.eustace.io/) for dependency management and packaging. To work with an editable install it\'s recommended that you setup `poetry` and install `archon` in a virtual environment by doing\n\n```console\npoetry install\n```\n\nPip does not support editable installs with PEP-517 yet. That means that running `pip install -e .` will fail because `poetry` doesn\'t use a `setup.py` file. As a workaround, you can use the `create_setup.py` file to generate a temporary `setup.py` file. To install `archon` in editable mode without `poetry`, do\n\n```console\npip install --pre poetry\npython create_setup.py\npip install -e .\n```\n\nNote that this will only install the production dependencies, not the development ones. You\'ll need to install those manually (see `pyproject.toml` `[tool.poetry.dev-dependencies]`). You will also need to return `create_setup.py` anytime the dependencies or metadata parameters in `pyproject.toml` change.\n\n### Style and type checking\n\nThis project uses the [black](https://github.com/psf/black) code style with 88-character line lengths for code and docstrings. It is recommended that you run `black` on save. Imports must be sorted using [isort](https://pycqa.github.io/isort/). The GitHub test workflow checks all the Python file to make sure they comply with the black formatting.\n\nConfiguration files for [flake8](https://flake8.pycqa.org/en/latest/), [isort](https://pycqa.github.io/isort/), and [black](https://github.com/psf/black) are provided and will be applied by most editors.\n\nFor Visual Studio Code, the following project file is compatible with the project configuration:\n\n```json\n{\n    "python.formatting.provider": "black",\n    "[python]" : {\n        "editor.codeActionsOnSave": {\n            "source.organizeImports": true\n        },\n        "editor.formatOnSave": true\n    },\n    "[markdown]": {\n        "editor.wordWrapColumn": 88\n    },\n    "[restructuredtext]": {\n        "editor.wordWrapColumn": 88\n    },\n    "editor.rulers": [88],\n    "editor.wordWrapColumn": 88,\n    "python.analysis.typeCheckingMode": "basic"\n}\n```\n\nThis assumes that the [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extensions are installed.\n\nThis project uses [type hints](https://docs.python.org/3/library/typing.html). Typing is enforced by the test workflow using [pyright](https://github.com/microsoft/pyright) (in practice this means that if ``Pylance`` doesn\'t produce any errors in basic mode, ``pyright`` shouldn\'t).\n',
    'author': 'José Sánchez-Gallego',
    'author_email': 'gallegoj@uw.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/sdss/archon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
