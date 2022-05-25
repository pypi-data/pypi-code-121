# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['quantumsymmetry', 'quantumsymmetry.qiskit_converter']

package_data = \
{'': ['*']}

install_requires = \
['ipython', 'numpy', 'openfermion', 'pyscf', 'qiskit', 'tabulate']

setup_kwargs = {
    'name': 'quantumsymmetry',
    'version': '0.1.28',
    'description': 'Quantum computing research package',
    'long_description': '# quantumsymmetry\n\nQuantum computing research package\n\n## Installation\n\n```bash\n$ pip install quantumsymmetry\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`quantumsymmetry` was created by Dario Picozzi. It is licensed under the terms of the GNU General Public License v3.0 license.\n\n## Credits\n\n`quantumsymmetry` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Dario Picozzi',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
