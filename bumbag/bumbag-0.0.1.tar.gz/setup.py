# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bumbag']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bumbag',
    'version': '0.0.1',
    'description': 'A package for Python utility functions.',
    'long_description': '# BumBag\n\n[![pypi](https://img.shields.io/pypi/v/bumbag)](https://pypi.org/project/bumbag)\n[![python](https://img.shields.io/badge/python-%5E3.8-blue)](https://pypi.org/project/bumbag)\n[![license](https://img.shields.io/pypi/l/bumbag)](https://github.com/estripling/bumbag/blob/main/LICENSE)\n[![ci status](https://github.com/estripling/bumbag/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/estripling/bumbag/actions/workflows/ci.yml)\n[![docs](https://readthedocs.org/projects/bumbag/badge/?version=latest)](https://readthedocs.org/projects/bumbag/?badge=latest)\n[![coverage](https://codecov.io/github/estripling/bumbag/coverage.svg?branch=main)](https://codecov.io/gh/estripling/bumbag)\n[![downloads](https://pepy.tech/badge/bumbag)](https://pepy.tech/project/bumbag)\n[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1&labelColor=ef8336)](https://pycqa.github.io/isort/)\n\n## About\n\nA package for Python utility functions.\n\n## Installation\n\n```bash\n$ pip install bumbag\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing?\nCheck out the contributing guidelines.\nPlease note that this project is released with a Code of Conduct.\nBy contributing to this project, you agree to abide by its terms.\n\n## License\n\n`bumbag` was created by BumBag Developers.\nIt is licensed under the terms of the BSD 3-Clause license.\n\n## Credits\n\n`bumbag` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the [`pypkgcookiecutter` template](https://github.com/estripling/pypkgcookiecutter).\n',
    'author': 'BumBag Developers',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/estripling/bumbag',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
