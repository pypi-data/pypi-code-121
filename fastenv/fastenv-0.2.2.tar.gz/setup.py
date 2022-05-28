# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastenv', 'fastenv.cloud']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.3,<4.0']

extras_require = \
{'all': ['httpx>=0.23,<0.24'],
 'cloud': ['httpx>=0.23,<0.24'],
 'httpx': ['httpx>=0.23,<0.24']}

setup_kwargs = {
    'name': 'fastenv',
    'version': '0.2.2',
    'description': 'Unified environment variable and settings management for FastAPI and beyond.',
    'long_description': '# ⚙️ fastenv 🚀\n\n_Unified environment variable and settings management for FastAPI and beyond_\n\n[![PyPI](https://img.shields.io/pypi/v/fastenv?color=success)](https://pypi.org/project/fastenv/)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=pytest&logoColor=white)](https://coverage.readthedocs.io/en/latest/)\n[![ci](https://github.com/br3ndonland/fastenv/workflows/ci/badge.svg)](https://github.com/br3ndonland/fastenv/actions/workflows/ci.yml)\n\n## Description\n\n[Environment variables](https://en.wikipedia.org/wiki/Environment_variable) are key-value pairs provided to the operating system with syntax like `VARIABLE_NAME=value`. Collections of environment variables are stored in files commonly named _.env_ and called "dotenv" files. The Python standard library `os` module provides tools for reading environment variables, such as `os.getenv("VARIABLE_NAME")`, but only handles strings, and doesn\'t include tools for file I/O. Additional logic is therefore needed to load environment variables from files before they can be read by Python, and to convert variables from strings to other Python types.\n\nThis project aims to:\n\n- [x] **Replace the aging [python-dotenv](https://github.com/theskumar/python-dotenv) project** with a similar, but more intuitive API, and modern syntax and tooling.\n- [x] **Implement asynchronous file I/O**. Reading and writing files can be done asynchronously with packages like [AnyIO](https://github.com/agronholm/anyio).\n- [x] **Implement asynchronous object storage integration**. Dotenv files are commonly kept in cloud object storage, but environment variable management packages typically don\'t integrate with object storage clients. Additional logic is therefore required to download _.env_ files from object storage prior to loading environment variables. This project aims to integrate with S3-compatible object storage, with a focus on downloading and uploading file objects.\n- [ ] **Read settings from TOML**. [It\'s all about _pyproject.toml_ now](https://snarky.ca/what-the-heck-is-pyproject-toml/). [Poetry](https://python-poetry.org/) has pushed [PEP 517](https://www.python.org/dev/peps/pep-0517/) build tooling and [PEP 518](https://www.python.org/dev/peps/pep-0518/) build requirements forward, and [even `setuptools` has come around](https://setuptools.readthedocs.io/en/latest/build_meta.html). [PEP 621](https://www.python.org/dev/peps/pep-0621/) defined how to store package metadata in _pyproject.toml_, and [PEP 631](https://www.python.org/dev/peps/pep-0631/) defined how to specify dependencies in _pyproject.toml_. Why don’t we use the metadata from our _pyproject.toml_ files in our Python applications?\n- [ ] **Unify settings management for FastAPI**. [Uvicorn](https://www.uvicorn.org/), [Starlette](https://www.starlette.io/config/), and _[pydantic](https://pydantic-docs.helpmanual.io/usage/settings/)_ each have their own ways of loading environment variables and configuring application settings. This means that, when [configuring a FastAPI application](https://fastapi.tiangolo.com/advanced/settings/), there are at least three different settings management tools available, each with their own pros and cons. It would be helpful to address the limitations of each of these options, potentially providing a similar, improved API for each one.\n\nThe source code is 100% type-annotated and unit-tested.\n\n## Quickstart\n\nInstall fastenv into a virtual environment:\n\n```sh\npython3 -m venv .venv\n. .venv/bin/activate\npython -m pip install fastenv\n```\n\nThen start a REPL session and try it out:\n\n```py\n.venv ❯ python\n\n# instantiate a DotEnv with a variable\n>>> import fastenv\n>>> dotenv = fastenv.DotEnv("EXAMPLE_VARIABLE=example_value")\n# add a variable with dictionary syntax\n>>> dotenv["ANOTHER_VARIABLE"] = "another_value"\n# delete a variable\n>>> del dotenv["ANOTHER_VARIABLE"]\n# add a variable by calling the instance\n>>> dotenv("I_THINK_FASTENV_IS=awesome")\n{\'I_THINK_FASTENV_IS\': \'awesome\'}\n# return a dict of the variables in the DotEnv instance\n>>> dict(dotenv)\n{\'EXAMPLE_VARIABLE\': \'example_value\', \'I_THINK_FASTENV_IS\': \'awesome\'}\n# save the DotEnv instance to a file\n>>> import anyio\n>>> anyio.run(fastenv.dump_dotenv, dotenv)\nPath(\'/path/to/this/dir/.env\')\n```\n\n## Documentation\n\nDocumentation is built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/), deployed on [Vercel](https://vercel.com/), and available at [fastenv.bws.bio](https://fastenv.bws.bio) and [fastenv.vercel.app](https://fastenv.vercel.app).\n\n[Vercel build configuration](https://vercel.com/docs/build-step):\n\n- Build command: `python3 -m pip install \'mkdocs-material>=8,<9\' && mkdocs build --site-dir public`\n- Output directory: `public` (default)\n\n[Vercel site configuration](https://vercel.com/docs/configuration) is specified in _vercel.json_.\n',
    'author': 'Brendon Smith',
    'author_email': 'bws@bws.bio',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/br3ndonland/fastenv',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
