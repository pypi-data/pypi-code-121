# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pycountstutorial', 'pycountstutorial.data']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.2,<4.0.0']

setup_kwargs = {
    'name': 'pycountstutorial',
    'version': '0.3.0',
    'description': 'Calculate word counts in a text file.',
    'long_description': '# PyCountsTutorial\n\n[![pypi](https://img.shields.io/pypi/v/pycountstutorial)](https://pypi.org/project/pycountstutorial)\n[![python](https://img.shields.io/badge/python-%5E3.8-blue)](https://pypi.org/project/pycountstutorial)\n[![license](https://img.shields.io/pypi/l/pycountstutorial)](https://github.com/estripling/pycountstutorial/blob/main/LICENSE)\n[![ci status](https://github.com/estripling/pycountstutorial/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/estripling/pycountstutorial/actions/workflows/ci.yml)\n[![docs](https://readthedocs.org/projects/pycountstutorial/badge/?version=latest)](https://readthedocs.org/projects/pycountstutorial/?badge=latest)\n[![coverage](https://codecov.io/github/estripling/pycountstutorial/coverage.svg?branch=main)](https://codecov.io/gh/estripling/pycountstutorial)\n[![downloads](https://pepy.tech/badge/pycountstutorial)](https://pepy.tech/project/pycountstutorial)\n[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1&labelColor=ef8336)](https://pycqa.github.io/isort/)\n\n## About\n\nCalculate word counts in a text file.\n\n## Installation\n\n```bash\n$ pip install pycountstutorial\n```\n\n## Usage\n\n`pycountstutorial` can be used to count words in a text file and plot results\nas follows:\n\n```python\nfrom pycountstutorial.core import count_words\nfrom pycountstutorial.plotting import plot_words\nimport matplotlib.pyplot as plt\n\nfile_path = "test.txt"  # path to your file\ncounts = count_words(file_path)\nfig = plot_words(counts, n=10)\nplt.show()\n```\n\n## Contributing\n\nInterested in contributing?\nCheck out the contributing guidelines.\nPlease note that this project is released with a Code of Conduct.\nBy contributing to this project, you agree to abide by its terms.\n\n## License\n\n`pycountstutorial` was created by PyCountsTutorial Developers.\nIt is licensed under the terms of the BSD 3-Clause license.\n\n## Credits\n\n`pycountstutorial` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the [`pypkgcookiecutter` template](https://github.com/estripling/pypkgcookiecutter).\n',
    'author': 'PyCountsTutorial Developers',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/estripling/pycountstutorial',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
