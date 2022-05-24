# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kapla',
 'kapla.cli',
 'kapla.core',
 'kapla.projects',
 'kapla.specs',
 'kapla.wrappers']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.5.0,<4.0.0',
 'chardet>=4.0.0,<5.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'rich>=11.2.0,<12.0.0',
 'ruamel.yaml>=0.17.20,<0.18.0',
 'structlog>=21.5.0,<22.0.0',
 'tomlkit>=0.9.2,<0.10.0']

extras_require = \
{':python_version < "3.9"': ['graphlib-backport>=1.0.3,<2.0.0']}

entry_points = \
{'console_scripts': ['k = kapla.cli:app']}

setup_kwargs = {
    'name': 'kapla-cli-v2',
    'version': '0.18.0',
    'description': '',
    'long_description': '# `kapla` project manager\n\n`kapla-cli` is a packaging and build system for Python codebases. It can be used to develop several python packages in a single repository, and easily manage shared dependencies accross the packages.\n\nIt relies on:\n  - venv\n  - pip\n  - poetry\n  - poetry-core @ master (pushed package from master branch as `quara-poetry-core-next` on 2022/03/03)\n\n## `poetry` and `pip` usage\n\n`poetry` is used in order to manage packages dependencies:\n\n- A pyproject.toml must exist at the root of the monorepo.\n- This pyproject.toml file use dependency groups to keep track of each package dependencies.\n- A single lock file is thus used to pin dependency versions accross all packages. \n    It avoids resolving dependency lock for each package, and shorten time required to update dependencies accross all packages.\n- Each package in the monorepo must have a valid `project.yml` file.\n- `project.yml` files are written according to a well known schema  (`KProjectSpec`).\n- At build or install time, `pyproject.toml` files are generated in each package directory from both the content of `project.yml` and the monorepo `pyproject.toml` file.\n- Packages are either built using `poetry build`.\n- Or installed using `pip install -e /path/to/package` (aka *editable install*). (See [PEP 660 -- Editable installs for pyproject.toml based builds](https://www.python.org/dev/peps/pep-0660/))\n\n> Packages are **not installed using Poetry**. Instead, `pip` is used to install packages in editable mode. This is possible using the master branch of `poetry-core` (not released yet)  which supports PEP 660 as `build system` for the editable install.\n\n## Why `poetry` ?\n\nPoetry is really powerful when it comes to declaring and resolving dependencies in a consistent manner. Without it, it would be difficult to ensure that all dependencies versions are compatible together.\n\n## Why `pip` and `editable` install ?\n\nEven though `poetry` provides an install feature out of the box, things can become quite slow when working with dozens of project.\n\nMoreover, `poetry` provide some support for local dependencies, the experience is far from optimal.\n\nBy using `pip` to install packages, it\'s possible to install several local dependencies in parallel without messing with `.venv/lib/pythonX.X/site-packages/` directory.\n\n# Quick Start\n\n## Virtual environment\n\n- Ensure a virtual environment exists at the root of a monorepo:\n\n```bash\nk venv\n```\n\n- Update pip toolkit within a virtual environment\n\n```bash\nk venv update\n```\n\n- Run a command within the virtual environment\n\n```bash\nk run python -c "import sys; print(sys.executable)"\n```\n\n## Global actions\n\n- Install all projects:\n\n```bash\nk install\n```\n\n- Install only two projects (and their dependencies)\n\n```bash\nk install pkg1 pkg2\n```\n\n- Build all projects\n\n```bash\nk build\n```\n\n- Build only two projects\n\n```bash\nk build pkg1 pkg2\n```\n\n## Projects actions\n\n- Add a project dependency (run the command from the package directory)\n\n```bash\nk project add package@version  # @version is optional\n```\n\n- Install the current project\n\n```bash\nk project install\n```\n\n- Show project dependencies\n\n```bash\nk project show [--latest] [--outdated] [--tree]\n```\n\n',
    'author': 'charbonnierg',
    'author_email': 'guillaume.charbonnier@araymond.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
