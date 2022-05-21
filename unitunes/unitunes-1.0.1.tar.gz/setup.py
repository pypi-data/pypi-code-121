# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unitunes',
 'unitunes.cli',
 'unitunes.eval',
 'unitunes.eval.data',
 'unitunes.services']

package_data = \
{'': ['*']}

install_requires = \
['musicbrainzngs>=0.7.1,<0.8.0',
 'pydantic>=1.9.0,<2.0.0',
 'ratelimit>=2.2.1,<3.0.0',
 'rich>=12.2.0,<13.0.0',
 'spotipy>=2.19.0,<3.0.0',
 'strsimpy>=0.2.1,<0.3.0',
 'tqdm>=4.64.0,<5.0.0',
 'typer[all]>=0.4.1,<0.5.0',
 'youtube-title-parse>=1.0.0,<2.0.0',
 'ytmusicapi>=0.21.0,<0.22.0']

entry_points = \
{'console_scripts': ['unitunes = unitunes.cli.cli:app']}

setup_kwargs = {
    'name': 'unitunes',
    'version': '1.0.1',
    'description': 'A CLI tool to manage playlists across music streaming services.',
    'long_description': '# unitunes [![PyPI version](https://badge.fury.io/py/unitunes.svg)](https://badge.fury.io/py/unitunes) ![example workflow](https://github.com/platers/unitunes/actions/workflows/github-actions.yml/badge.svg)\n\n![unituneslogo](https://github.com/platers/unitunes/blob/master/unitunes.png?raw=true)\n\nA command-line interface tool to manage playlists across music streaming services.\n\n![demo](demo.gif)\n\n## Introduction\n\nunitunes manages playlists across streaming services. unitunes can transfer songs between services and keep playlists in sync.\n\nunitunes stores your playlists in plain text, allowing you to version control your music. Playlists can be pushed and pulled from streaming services. Tracks from one service can be searched on another.\n\n### Current Supported Streaming Services\n\n| Name          | Pullable | Pushable | Searchable |\n| ------------- | :------: | :------: | :--------: |\n| MusicBrainz   |          |          |     ✅     |\n| Spotify       |    ✅    |    ✅    |     ✅     |\n| Youtube Music |    ✅    |    ✅    |     ✅     |\n\nWant to add support for another service? See [contributing](#contributing).\n\n## Documentation\n\n[Documentation](https://github.com/platers/unitunes/blob/master/docs.md)\n\n## Quickstart\n\n### Installation\n\n```bash\npip install unitunes\n```\n\n### Initialize\n\n```bash\nunitunes init\n```\n\nThis creates a `config.json` file in the current directory.\n\n### Add Services\n\n#### Spotify\n\nFollow the instructions at https://spotipy.readthedocs.io/en/2.19.0/#getting-started to obtain client credentials.\n\nPut the credentials in a file like so:\n\n```json\n{\n  "client_id": "...",\n  "client_secret": "...",\n  "redirect_uri": "http://example.com"\n}\n```\n\nRegister the service in unitunes:\n\n```bash\nunitunes service add spotify spotify_config.json\n```\n\n#### Youtube Music\n\nFollow the instructions at https://ytmusicapi.readthedocs.io/en/latest/setup.html#manual-file-creation to create a `ytm_config.json` file.\n\nRegister the service in unitunes:\n\n```bash\nunitunes service add ytm ytm_config.json\n```\n\n### Add Playlists\n\nInitialize UP\'s from your existing playlists:\n\n```bash\nunitunes fetch spotify # use -f to skip confirmation\nunitunes fetch ytm\n```\n\n### Pull Playlists\n\nPull all tracks from all playlists.\n\n```bash\nunitunes pull\n```\n\n### Search Playlists\n\nSearch for tracks on another service:\n\n```bash\nunitunes search SERVICE_TYPE PLAYLIST_NAME\n```\n\n### Push Playlists\n\nPush all changes to streaming services:\n\n```bash\nunitunes push\n```\n\n## Contributing\n\nunitunes is in alpha. Contributions are very welcome. I am looking for collaborators to grow unitunes into a foundation for user controlled music software.\n\nTake a look at the open issues!\n\n### Development Setup\n\n1. Fork and clone the repository.\n2. Install [poetry](https://python-poetry.org/).\n3. In the root directory, run `poetry shell`.\n4. Run `poetry install`.\n5. `unitunes` should now be runnable.\n\n#### Testing\n\nRun `pytest` to run tests. With no arguments, it will skip tests that require service configs.\n\nAdd a service config to run more tests.\n\n```bash\npytest --spotify spotify_config.json --ytm ytm_config.json # may need to run with -s to paste spotify redirect URL the first time\n```\n',
    'author': 'platers',
    'author_email': 'platers81@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/platers/unitunes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
