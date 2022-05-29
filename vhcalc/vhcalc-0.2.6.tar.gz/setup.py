# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vhcalc', 'vhcalc.services', 'vhcalc.tools']

package_data = \
{'': ['*']}

install_requires = \
['Distance>=0.1.3,<0.2.0',
 'ImageHash>=4.2.1,<5.0.0',
 'Pillow>=9.1.1',
 'bitstring>=3.1.9,<4.0.0',
 'click-path>=0.0.5,<0.0.6',
 'click-pathlib>=2020.3.13,<2021.0.0',
 'click==8.0.4',
 'colorama==0.4.4',
 'imageio-ffmpeg>=0.4.5,<0.5.0',
 'loguru>=0.6.0,<0.7.0',
 'numpy>=1.22.3,<2.0.0',
 'rich[spinner]>=11.2.0,<12.0.0']

entry_points = \
{'console_scripts': ['export_imghash_from_media = '
                     'vhcalc.app:export_imghash_from_media',
                     'vhcalc = vhcalc.app:cli']}

setup_kwargs = {
    'name': 'vhcalc',
    'version': '0.2.6',
    'description': "It's a client-side library that implements a custom algorithm for extracting video hashes (fingerprints) from any video source.",
    'long_description': "[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)\n[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Github Actions](https://github.com/yoyonel/vhcalc/actions/workflows/python-check.yaml/badge.svg)](https://github.com/yoyonel/vhcalc/wayback-machine-saver/actions/workflows/python-check.yaml)\n\n[![PyPI Package latest release](https://img.shields.io/pypi/v/vhcalc.svg?style=flat-square)](https://pypi.org/project/vhcalc/)\n[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/vhcalc?style=flat-square)](https://pypi.org/project/vhcalc/)\n[![Supported versions](https://img.shields.io/pypi/pyversions/vhcalc.svg?style=flat-square)](https://pypi.org/project/vhcalc/)\n\n[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/yoyonel/vhcalc?sort=semver)](https://hub.docker.com/r/yoyonel/vhcalc/)\n\n[![Coverage Status](https://coveralls.io/repos/github/yoyonel/vhcalc/badge.svg?branch=main)](https://coveralls.io/github/yoyonel/vhcalc?branch=main)\n\n# vhcalc\n\nIt's a client-side library that implements a custom algorithm for extracting video hashes (fingerprints) from any video source.\n\n## Getting Started\n\n### Prerequisites\n* [Python](https://www.python.org/downloads/)\n\n## Usage\n\n```sh\n$ export_imghash_from_media --help  \nUsage: export_imghash_from_media [OPTIONS]\n\n  This script exporting binary images hashes (fingerprints) from (any) media\n  (video file)\n\nOptions:\n  --version                       Show the version and exit.\n  -r, --medias_pattern PATH-OR-GLOB\n                                  Pattern to find medias  [required]\n  -o, --output-file PATH          File where to write images hashes.\n  --help                          Show this message and exit.\n```\n\n\n## Docker\n\nDocker hub: [yoyonel/vhcalc](https://hub.docker.com/r/yoyonel/vhcalc/)\n\n```sh\n$ docker run -it yoyonel/vhcalc:main --help\nUsage: export_imghash_from_media [OPTIONS]\n\n  This script exporting binary images hashes (fingerprints) from (any) media\n  (video file)\n\nOptions:\n  --version                       Show the version and exit.\n  -r, --medias_pattern PATH-OR-GLOB\n                                  Pattern to find medias  [required]\n  -o, --output-file PATH          File where to write images hashes.\n  --help                          Show this message and exit.\n```\n\n## Contributing\nSee [Contributing](contributing.md)\n\n## Authors\nLionel Atty <yoyonel@hotmail.com>\n\n\nCreated from [Lee-W/cookiecutter-python-template](https://github.com/Lee-W/cookiecutter-python-template/tree/1.1.2) version 1.1.2\n",
    'author': 'Lionel Atty',
    'author_email': 'yoyonel@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yoyonel/vhcalc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
