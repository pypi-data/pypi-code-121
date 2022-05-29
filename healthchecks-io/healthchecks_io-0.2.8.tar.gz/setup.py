# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['healthchecks_io', 'healthchecks_io.client', 'healthchecks_io.schemas']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'croniter>=1.1.0,<2.0.0',
 'httpx>=0.21.1,<0.24.0',
 'pydantic>=1.8.2,<2.0.0',
 'pytz>=2021.3,<2023.0']

setup_kwargs = {
    'name': 'healthchecks-io',
    'version': '0.2.8',
    'description': 'A python client package for Healthchecks.io API',
    'long_description': "Py Healthchecks.Io\n==================\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/healthchecks-io.svg\n   :target: https://pypi.org/project/healthchecks-io/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/healthchecks-io.svg\n   :target: https://pypi.org/project/healthchecks-io/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/healthchecks-io\n   :target: https://pypi.org/project/healthchecks-io\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/healthchecks-io\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/py-healthchecksio/latest.svg?label=Read%20the%20Docs\n   :target: https://py-healthchecksio.readthedocs.io/en/latest/\n   :alt: Read the documentation at https://py-healthchecksio.readthedocs.io/en/latest/\n.. |Tests| image:: https://github.com/andrewthetechie/py-healthchecks.io/workflows/Tests/badge.svg\n   :target: https://github.com/andrewthetechie/py-healthchecks.io/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/andrewthetechie/py-healthchecks.io/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/andrewthetechie/py-healthchecks.io\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\nA python client for healthchecks.io. Supports the management api and ping api.\n\nFeatures\n--------\n\n* Sync and Async clients based on HTTPX\n* Supports the management api and the ping api\n* Supports Healthchecks.io SAAS and self-hosted instances\n\n\nRequirements\n------------\n\n* httpx\n* pytz\n* pydantic\n\n\nInstallation\n------------\n\nYou can install *Py Healthchecks.Io* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install healthchecks-io\n\n\nUsage\n-----\n\nPlease see the `Usage <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*Py Healthchecks.Io* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/andrewthetechie/py-healthchecks.io/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://py-healthchecksio.readthedocs.io/en/latest/usage.html\n",
    'author': 'Andrew Herrington',
    'author_email': 'andrew.the.techie@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrewthetechie/py-healthchecks.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
