# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deluge_card', 'tests']

package_data = \
{'': ['*'],
 'tests': ['fixtures/*',
           'fixtures/DC01/KITS/*',
           'fixtures/DC01/SAMPLES/Artists/A/*',
           'fixtures/DC01/SAMPLES/CLASSIC/DX7/*',
           'fixtures/DC01/SAMPLES/DRUMS/Kick/*',
           'fixtures/DC01/SAMPLES/Kick/*',
           'fixtures/DC01/SAMPLES/MV/*',
           'fixtures/DC01/SONGS/*',
           'fixtures/DC01/SYNTHS/*',
           'fixtures/DC02/KITS/*',
           'fixtures/DC02/SAMPLES/DRUMS/Rabid-Elephant-Portal-Drum Samples/*',
           'fixtures/DC02/SAMPLES/MV/*',
           'fixtures/DC02/SAMPLES/Multisamples/WaldorfM/Loopop-Waldorf-M-4-StereoSizzle '
           'Samples/*',
           'fixtures/DC02/SONGS/*',
           'fixtures/DC02/SONGS/A/*',
           'fixtures/DC02/SYNTHS/*']}

install_requires = \
['lxml>=4.8.0,<5.0.0', 'pydel>=0.5.3,<0.6.0']

setup_kwargs = {
    'name': 'deluge-card',
    'version': '0.7.0',
    'description': 'python api for synthstrom deluge cards from fw3.15+.',
    'long_description': '# deluge-card\n\n\n[![pypi](https://img.shields.io/pypi/v/deluge-card.svg)](https://pypi.org/project/deluge-card/)\n[![python](https://img.shields.io/pypi/pyversions/deluge-card.svg)](https://pypi.org/project/deluge-card/)\n[![Build Status](https://github.com/mupaduw/deluge-card/actions/workflows/dev.yml/badge.svg)](https://github.com/mupaduw/deluge-card/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/mupaduw/deluge-card/branch/main/graphs/badge.svg)](https://codecov.io/github/mupaduw/deluge-card)\n\n\n\nA Python3 api for Synthstrom Audible Deluge SD cards.\n\n* Documentation: <https://mupaduw.github.io/deluge-card>\n* GitHub: <https://github.com/mupaduw/deluge-card>\n* PyPI: <https://pypi.org/project/deluge-card/>\n* Free software: MIT\n\n\n## Features\n\n* List sub-folders that resemble Deluge cards (DelugeCardFS).\n* List contents of deluge filesystems (cards , folders).\n* Get details of card contents: songs, samples, sample usage.\n* Get song details like **tempo**, **key**, **scale**.\n* Filter contents by paths, using posix **ls** glob patterns.\n* Move samples like posix **mv**.\n* Unit tested on Macosx, Linux & Windows, Python 3.8+.\n* Song XML from fw3.15.\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n',
    'author': 'Chris Chamberlain',
    'author_email': 'chrisbc@artisan.co.nz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mupaduw/deluge-card',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
