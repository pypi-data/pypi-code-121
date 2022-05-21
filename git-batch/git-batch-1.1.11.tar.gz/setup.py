# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitbatch']

package_data = \
{'': ['*']}

install_requires = \
['GitPython==3.1.27', 'colorama==0.4.4', 'python-json-logger==2.0.2']

entry_points = \
{'console_scripts': ['git-batch = gitbatch.cli:main']}

setup_kwargs = {
    'name': 'git-batch',
    'version': '1.1.11',
    'description': 'Clone single branch from all repositories listed in a file.',
    'long_description': '# git-batch\n\nAutomate cloning a single branch from a list of repositories\n\n[![Build Status](https://img.shields.io/drone/build/thegeeklab/git-batch?logo=drone&server=https%3A%2F%2Fdrone.thegeeklab.de)](https://drone.thegeeklab.de/thegeeklab/git-batch)\n[![Docker Hub](https://img.shields.io/badge/dockerhub-latest-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/thegeeklab/git-batch)\n[![Quay.io](https://img.shields.io/badge/quay-latest-blue.svg?logo=docker&logoColor=white)](https://quay.io/repository/thegeeklab/git-batch)\n[![Python Version](https://img.shields.io/pypi/pyversions/git-batch.svg)](https://pypi.org/project/git-batch/)\n[![PyPi Status](https://img.shields.io/pypi/status/git-batch.svg)](https://pypi.org/project/git-batch/)\n[![PyPi Release](https://img.shields.io/pypi/v/git-batch.svg)](https://pypi.org/project/git-batch/)\n[![GitHub contributors](https://img.shields.io/github/contributors/thegeeklab/git-batch)](https://github.com/thegeeklab/git-batch/graphs/contributors)\n[![Source: GitHub](https://img.shields.io/badge/source-github-blue.svg?logo=github&logoColor=white)](https://github.com/thegeeklab/git-batch)\n[![License: MIT](https://img.shields.io/github/license/thegeeklab/git-batch)](https://github.com/thegeeklab/git-batch/blob/main/LICENSE)\n\nSimple tool to automate cloning a single branch from a list of repositories.\n\n## Contributors\n\nSpecial thanks goes to all [contributors](https://github.com/thegeeklab/git-batch/graphs/contributors). If you would like to contribute,\nplease see the [instructions](https://github.com/thegeeklab/git-batch/blob/main/CONTRIBUTING.md).\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE](https://github.com/thegeeklab/git-batch/blob/main/LICENSE) file for details.\n',
    'author': 'Robert Kaussow',
    'author_email': 'mail@thegeeklab.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thegeeklab/git-batch/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
