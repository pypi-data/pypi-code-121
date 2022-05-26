# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['napalm_fsos_ssh']

package_data = \
{'': ['*'], 'napalm_fsos_ssh': ['utils/textfsm_templates/*']}

install_requires = \
['napalm>=3.4.1,<4.0.0']

setup_kwargs = {
    'name': 'napalm-fsos-ssh',
    'version': '0.1.0',
    'description': 'Napalm driver for FSOS through SSH',
    'long_description': 'Napalm driver for FSOS using SSH\n\n[![PyPI](https://img.shields.io/pypi/v/napalm-fsos-ssh.svg)](https://pypi.python.org/pypi/napalm-fsos-ssh)\n[![PyPI versions](https://img.shields.io/pypi/pyversions/napalm-fsos-ssh.svg)](https://pypi.python.org/pypi/napalm-fsos-ssh)\n[![Actions Build](https://github.com/M0NsTeRRR/napalm-fsos/workflows/Python%20test/badge.svg)](https://github.com/M0NsTeRRR/napalm-fsos-ssh/blob/main/.github/workflows/test.yml)\n[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n# Warning\nThis driver has been tested only on S3900 24T4S\n\n# Install\n```\npip install napalm-fsos-ssh\n```\n\n# Dev\nInstall [Poetry](https://python-poetry.org/docs/master/#installing-with-the-official-installer) with version >= 1.2.0a1\n\nInstall and setup dependencies\n```\npoetry install\npoetry shell\npre-commit install\n```\n\n### Run unit test\n```\npytest\n```\n\n### Run pre-commit\n```\npre-commit run --all-files\n```\n\n# Switch configuration\n\nIn order to use the driver you need to enable ssh:\n```\nip ssh server enable\n```\n\nYou also need to configure a username and password with ro permission to authenticate with ssh\n```\nusername <your_username> privilege 0\nusername <your_username> password 0 <your_password>\n```\n\n# Licence\n\nThe code is under CeCILL license.\n\nYou can find all details here: https://cecill.info/licences/Licence_CeCILL_V2.1-en.html\n\n# Credits\n\nCopyright © Ludovic Ortega, 2022\n\nContributor(s):\n\n-Ortega Ludovic - ludovic.ortega@adminafk.fr\n',
    'author': 'Ludovic Ortega',
    'author_email': 'ludovic.ortega@adminafk.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/M0NsTeRRR/napalm-fsos-ssh',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
