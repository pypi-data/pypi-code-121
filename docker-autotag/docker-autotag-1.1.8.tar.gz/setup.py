# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dockerautotag']

package_data = \
{'': ['*']}

install_requires = \
['colorama==0.4.4', 'python-json-logger==2.0.2', 'semantic-version==2.9.0']

entry_points = \
{'console_scripts': ['docker-autotag = dockerautotag.cli:main']}

setup_kwargs = {
    'name': 'docker-autotag',
    'version': '1.1.8',
    'description': 'Creates a list of docker tags from a given version string.',
    'long_description': "# docker-autotag\n\nCreate docker tags from a given version string\n\n[![Build Status](https://img.shields.io/drone/build/thegeeklab/docker-autotag?logo=drone&server=https%3A%2F%2Fdrone.thegeeklab.de)](https://drone.thegeeklab.de/thegeeklab/docker-autotag)\n[![Docker Hub](https://img.shields.io/badge/dockerhub-latest-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/thegeeklab/docker-autotag)\n[![Quay.io](https://img.shields.io/badge/quay-latest-blue.svg?logo=docker&logoColor=white)](https://quay.io/repository/thegeeklab/docker-autotag)\n[![Python Version](https://img.shields.io/pypi/pyversions/docker-autotag.svg)](https://pypi.org/project/docker-autotag/)\n[![PyPi Status](https://img.shields.io/pypi/status/docker-autotag.svg)](https://pypi.org/project/docker-autotag/)\n[![PyPi Release](https://img.shields.io/pypi/v/docker-autotag.svg)](https://pypi.org/project/docker-autotag/)\n[![GitHub contributors](https://img.shields.io/github/contributors/thegeeklab/docker-autotag)](https://github.com/thegeeklab/docker-autotag/graphs/contributors)\n[![Source: GitHub](https://img.shields.io/badge/source-github-blue.svg?logo=github&logoColor=white)](https://github.com/thegeeklab/docker-autotag)\n[![License: MIT](https://img.shields.io/github/license/thegeeklab/docker-autotag)](https://github.com/thegeeklab/docker-autotag/blob/main/LICENSE)\n\nSimple tool to create a list of docker tags from a given version string.\n\n## Environment variables\n\n```Shell\n# if not set a comma-separated list will be printed to stdout\nDOCKER_AUTOTAG_OUTPUT_FILE=\n# adds a given suffix to every determined tag\nDOCKER_AUTOTAG_SUFFIX=\n# version string to use; returns 'latest' if nothing is specified\nDOCKER_AUTOTAG_VERSION=\n# comma-seprated list of static tags to add to the result set\nDOCKER_AUTOTAG_EXTRA_TAGS=\n# 'latest' tag would only be used if determined tag list is empty; adds always 'latest' to the result\nDOCKER_AUTOTAG_FORCE_LATEST=False\n# if the given version string contains a prerelease, no other tags will be returned\nDOCKER_AUTOTAG_IGNORE_PRERELEASE=False\n```\n\n## Examples\n\n```Shell\nDOCKER_AUTOTAG_VERSION=1.0.1 docker-autotag\n# 1.0.1,1.0,1\n\nDOCKER_AUTOTAG_VERSION=0.1.0 docker-autotag\n# 0.1.0, 0.1\n\n## 'v' prefixes e.g. from git tags will be removed\nDOCKER_AUTOTAG_VERSION=v1.0.1 docker-autotag\n# 1.0.1,1.0,1\n\n## unsufficient semver version strings will be tried to convert automatically\n## if conversion doesn't work return 'latest'\nDOCKER_AUTOTAG_VERSION=1.0 docker-autotag\n# 1.0.0,1.0,1\n\nDOCKER_AUTOTAG_VERSION=1.0.0-beta docker-autotag\n# 1.0.0-beta\n\n## ignore prerelease to always get a full list of tags\nDOCKER_AUTOTAG_IGNORE_PRERELEASE=True DOCKER_AUTOTAG_VERSION=1.0.0-beta docker-autotag\n# 1.0.0-beta,1.0.0,1.0,1\n\nDOCKER_AUTOTAG_SUFFIX=amd64 DOCKER_AUTOTAG_VERSION=1.0.0 docker-autotag\n# 1.0.0,1.0,1,1.0.0-amd64,1.0-amd64,1-amd64\n\nDOCKER_AUTOTAG_EXTRA_TAGS=extra1,extra2 DOCKER_AUTOTAG_VERSION=1.0.0 docker-autotag\n# 1.0.0,1.0,1,extra1,extra2\n```\n\n## Contributors\n\nSpecial thanks goes to all [contributors](https://github.com/thegeeklab/docker-autotag/graphs/contributors). If you would like to contribute,\nplease see the [instructions](https://github.com/thegeeklab/docker-autotag/blob/main/CONTRIBUTING.md).\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE](https://github.com/thegeeklab/docker-autotag/blob/main/LICENSE) file for details.\n",
    'author': 'Robert Kaussow',
    'author_email': 'mail@thegeeklab.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thegeeklab/docker-autotag/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
