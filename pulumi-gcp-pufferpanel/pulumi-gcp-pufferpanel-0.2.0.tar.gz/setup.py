# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pulumi_gcp_pufferpanel', 'pulumi_gcp_pufferpanel.cloud_function']

package_data = \
{'': ['*']}

install_requires = \
['pulumi-gcp>=6.23.0,<7.0.0']

setup_kwargs = {
    'name': 'pulumi-gcp-pufferpanel',
    'version': '0.2.0',
    'description': 'Pulumi ComponentResource for running PufferPanel on GCP',
    'long_description': '\n# GCP PufferPanel\n\n[![PyPI - Version](https://img.shields.io/pypi/v/pulumi-gcp-pufferpanel.svg)](https://pypi.python.org/pypi/pulumi-gcp-pufferpanel)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pulumi-gcp-pufferpanel.svg)](https://pypi.python.org/pypi/pulumi-gcp-pufferpanel)\n[![Tests](https://github.com/briankanya/pulumi-gcp-pufferpanel/workflows/tests/badge.svg)](https://github.com/briankanya/pulumi-gcp-pufferpanel/actions?workflow=tests)\n[![Codecov](https://codecov.io/gh/briankanya/pulumi-gcp-pufferpanel/branch/master/graph/badge.svg?token=W5Z7N8OUTW)](https://codecov.io/gh/briankanya/pulumi-gcp-pufferpanel)\n\n[![Read the Docs](https://readthedocs.org/projects/pulumi-gcp-pufferpanel/badge/)](https://pulumi-gcp-pufferpanel.readthedocs.io/)\n[![PyPI - License](https://img.shields.io/pypi/l/pulumi-gcp-pufferpanel.svg)](https://pypi.python.org/pypi/pulumi-gcp-pufferpanel)\n\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n## Description\n\nPulumi ComponentResource for running [PufferPanel](https://github.com/PufferPanel/PufferPanel) on GCP\n\n## Useful links\n\n* GitHub repo: <https://github.com/briankanya/pulumi-gcp-pufferpanel>\n* Documentation: <https://pulumi-gcp-pufferpanel.readthedocs.io>\n* Free software: GNU General Public License v3\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter][cookiecutter] and the [fedejaure/cookiecutter-modern-pypackage][cookiecutter-modern-pypackage] project template.\n\n[cookiecutter]: https://github.com/cookiecutter/cookiecutter\n[cookiecutter-modern-pypackage]: https://github.com/fedejaure/cookiecutter-modern-pypackage\n',
    'author': 'Brian Kanya',
    'author_email': 'briankanya@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/briankanya/pulumi-gcp-pufferpanel',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
