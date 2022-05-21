# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dockertidy',
 'dockertidy.test',
 'dockertidy.test.fixtures',
 'dockertidy.test.unit']

package_data = \
{'': ['*']}

install_requires = \
['anyconfig==0.13.0',
 'appdirs==1.4.4',
 'certifi==2022.5.18.1',
 'colorama==0.4.4',
 'dateparser==1.1.1',
 'docker-pycreds==0.4.0',
 'docker==5.0.3',
 'environs==9.5.0',
 'idna==3.3',
 'ipaddress==1.0.23',
 'jsonschema==4.5.1',
 'nested-lookup==0.2.23',
 'pathspec==0.9.0',
 'python-dateutil==2.8.2',
 'python-json-logger==2.0.2',
 'requests==2.27.1',
 'ruamel.yaml==0.17.21',
 'websocket_client==1.3.2',
 'zipp==3.8.0']

entry_points = \
{'console_scripts': ['docker-tidy = dockertidy.cli:main']}

setup_kwargs = {
    'name': 'docker-tidy',
    'version': '1.1.16',
    'description': 'Keep docker hosts tidy.',
    'long_description': '# docker-tidy\n\nKeep docker hosts tidy\n\n[![Build Status](https://img.shields.io/drone/build/thegeeklab/docker-tidy?logo=drone&server=https%3A%2F%2Fdrone.thegeeklab.de)](https://drone.thegeeklab.de/thegeeklab/docker-tidy)\n[![Docker Hub](https://img.shields.io/badge/docker-latest-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/thegeeklab/docker-tidy)\n[![Python Version](https://img.shields.io/pypi/pyversions/docker-tidy.svg)](https://pypi.org/project/docker-tidy/)\n[![PyPI Status](https://img.shields.io/pypi/status/docker-tidy.svg)](https://pypi.org/project/docker-tidy/)\n[![PyPI Release](https://img.shields.io/pypi/v/docker-tidy.svg)](https://pypi.org/project/docker-tidy/)\n[![Codecov](https://img.shields.io/codecov/c/github/thegeeklab/docker-tidy)](https://codecov.io/gh/thegeeklab/docker-tidy)\n[![GitHub contributors](https://img.shields.io/github/contributors/thegeeklab/docker-tidy)](https://github.com/thegeeklab/docker-tidy/graphs/contributors)\n[![Source: GitHub](https://img.shields.io/badge/source-github-blue.svg?logo=github&logoColor=white)](https://github.com/thegeeklab/docker-tidy)\n[![License: Apache-2.0](https://img.shields.io/github/license/thegeeklab/docker-tidy)](https://github.com/thegeeklab/docker-tidy/blob/main/LICENSE)\n\nThis project is a fork of [Yelp/docker-custodian](https://github.com/Yelp/docker-custodian). Keep docker hosts tidy.\n\nYou can find the full documentation at [https://docker-tidy.geekdocs.de](https://docker-tidy.geekdocs.de/).\n\n## Contributors\n\nSpecial thanks goes to all [contributors](https://github.com/thegeeklab/docker-tidy/graphs/contributors). If you would like to contribute,\nplease see the [instructions](https://github.com/thegeeklab/docker-tidy/blob/main/CONTRIBUTING.md).\n\n## License\n\nThis project is licensed under the Apache-2.0 License - see the [LICENSE](https://github.com/thegeeklab/docker-tidy/blob/main/LICENSE) file for details.\n',
    'author': 'Robert Kaussow',
    'author_email': 'mail@thegeeklab.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://docker-tidy.geekdocs.de/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
