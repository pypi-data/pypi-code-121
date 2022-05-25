# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tessif']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'tessif',
    'version': '0.0.10',
    'description': 'Transforming Energy Supply System modell*I*ng Framework',
    'long_description': 'Tessif\n======\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/tessif.svg\n   :target: https://pypi.org/project/tessif/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/tessif.svg\n   :target: https://pypi.org/project/tessif/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/tessif\n   :target: https://pypi.org/project/tessif\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/tessif\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/tessif/latest.svg?label=Read%20the%20Docs\n   :target: https://tessif.readthedocs.io/\n   :alt: Read the documentation at https://tessif.readthedocs.io/\n.. |Tests| image:: https://github.com/tZ3ma/tessif/workflows/Tests/badge.svg\n   :target: https://github.com/tZ3ma/tessif/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/tZ3ma/tessif/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/tZ3ma/tessif\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\n\nTransforming Energy Suppy System modell*I*ng Framework\n\nLatest Stable Version\n---------------------\nYou can install *Tessif* via pip_ from PyPI_.\nInstall using a console with your virtual environment activated:\n\n.. code-block:: console\n\n   $ pip install tesif\n\nLatest Development Version (potentially unstable)\n-------------------------------------------------\n\nYou can install the development version of *Tessif* via pip_ from TestPyPI_.\nInstall using a console with your virtual environment activated:\n\n.. code-block:: console\n\n   $ pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ tessif\n\nThis installs the TestPyPI_ version of tessif while resolving the dependencies on PyPI_.\n\nLicense\n-------\nDistributed under the terms of the `MIT license`_,\n*Tessif* is free and open source software.\n\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _TestPyPI: https://test.pypi.org/\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://tessif.readthedocs.io/en/latest/usage.html\n',
    'author': 'Mathias Ammon',
    'author_email': 'mathias.ammon@tuhh.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tZ3ma/tessif',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
