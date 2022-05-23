# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinx_carousel']

package_data = \
{'': ['*'], 'sphinx_carousel': ['_static/*']}

install_requires = \
['Sphinx>=4.0.0']

setup_kwargs = {
    'name': 'sphinx-carousel',
    'version': '1.1.0',
    'description': 'A Sphinx extension for creating slideshows using Bootstrap Carousels.',
    'long_description': '# sphinx-carousel\n\n[![Github-CI][github-ci]][github-link]\n[![Coverage Status][codecov-badge]][codecov-link]\n[![Documentation Status][rtd-badge]][rtd-link]\n[![Code style: black][black-badge]][black-link]\n[![PyPI][pypi-badge]][pypi-link]\n\n[github-ci]: https://github.com/Robpol86/sphinx-carousel/actions/workflows/ci.yml/badge.svg?branch=main\n[github-link]: https://github.com/Robpol86/sphinx-carousel/actions/workflows/ci.yml\n[codecov-badge]: https://codecov.io/gh/Robpol86/sphinx-carousel/branch/main/graph/badge.svg\n[codecov-link]: https://codecov.io/gh/Robpol86/sphinx-carousel\n[rtd-badge]: https://readthedocs.org/projects/sphinx-carousel/badge/?version=latest\n[rtd-link]: https://sphinx-carousel.readthedocs.io/en/latest/?badge=latest\n[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg\n[black-link]: https://github.com/ambv/black\n[pypi-badge]: https://img.shields.io/pypi/v/sphinx-carousel.svg\n[pypi-link]: https://pypi.org/project/sphinx-carousel\n\nA Sphinx extension for creating slideshows using\n[Bootstrap 5 Carousels](https://getbootstrap.com/docs/5.1/components/carousel/).\n\n📖 See the documentation at https://sphinx-carousel.readthedocs.io\n\n## Install\n\nRequires Python 3.6 or greater and Sphinx 4.0 or greater.\n\n```shell\npip install sphinx-carousel\n```\n\n## Example\n\n```python\n# conf.py\nextensions = [\n    "sphinx_carousel.carousel",\n]\n```\n\n```rst\n===============\nAn RST Document\n===============\n\n.. carousel::\n\n    .. image:: https://i.imgur.com/fmJnevTl.jpg\n        :target: https://i.imgur.com/fmJnevT.jpg\n    .. image:: https://i.imgur.com/ppGH90Jl.jpg\n    .. figure:: https://i.imgur.com/fWyn9A2l.jpg\n\n        An Example Image\n\n        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut\n        labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris\n        nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit\n        esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt\n        in culpa qui officia deserunt mollit anim id est laborum.\n\n```\n',
    'author': 'Robpol86',
    'author_email': 'robpol86@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
