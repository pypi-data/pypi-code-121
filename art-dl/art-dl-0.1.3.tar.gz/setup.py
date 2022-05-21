# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['art_dl', 'art_dl.sites', 'art_dl.sites.deviantart', 'art_dl.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0',
 'aiohttp-socks[asyncio]>=0.7.1,<0.8.0',
 'aiohttp>=3.8.1,<4.0.0',
 'lxml>=4.8.0,<5.0.0']

entry_points = \
{'console_scripts': ['art-dl = art_dl:main']}

setup_kwargs = {
    'name': 'art-dl',
    'version': '0.1.3',
    'description': 'Artworks downloader',
    'long_description': '# Artworks downloader\n\n## Supported sites\n\n- artstation.com [#usage](#sites-with-simple-usage)\n- deviantart.com [#usage](#deviantart)\n- imgur.com [#usage](#sites-with-simple-usage)\n- pixiv.net [#usage](#sites-with-simple-usage) [#notes](#pixiv)\n  - zettai.moe\n- reddit.com [#usage](#sites-with-simple-usage)\n- twitter.com [#usage](#sites-with-simple-usage) [#notes](#twitter)\n- wallhaven.cc [#usage](#sites-with-simple-usage) [#notes](#wallhaven)\n\n[Supported URL types](#supported-url-types)\n\n## Install\n\n### With `pip`\n\n```sh\npip install art-dl\n```\n\nThen run as `art-dl` [#usage](#usage)\n\n### Build from source\n\nYou need poetry, [install](https://python-poetry.org/docs/#installation) it, then run from inside the project\n\n```sh\npoetry install --no-dev\n\n# run with poetry\npoetry run python -m art_dl\n\n# enter venv created with poetry\npoetry shell\n# run inside it as\npython -m art_dl\n# or\nart-dl\n\n# create and activate venv, e.g. with virtualenvwrapper, then\npoetry install --no-dev\nart-dl\n```\n\n## Usage\n\n```\nusage: art-dl [-h] [-u URL] [-l LIST] [--folder FOLDER] [--action ACTION] [-q] [-v] [--version]\n\nArtworks downloader\n\noptions:\n  -h, --help            show this help message and exit\n  -u URL, --url URL     URL to download\n  -l LIST, --list LIST  File with list of URLs to download\n  --folder FOLDER       Folder to save artworks. Default folder - data\n  --action ACTION\n  -q, --quiet           Do not show logs\n  -v, --verbose         Show more logs\n  --version             Show version\n```\n\n### Sites with simple usage\n\nJust run\n\n```sh\nart-dl -u [URL here]\n```\n\n### DeviantArt\n\nYou should have deviantart.com account, login to it, then\n\n- register an application\n  - go to https://www.deviantart.com/developers/apps\n  - click "Register Application"\n  - in field "OAuth2 Redirect URI Whitelist (Required)" under "Application Settings" block paste `http://localhost:23445`\n  - scroll to bottom and check "I have read and agree to the API License Agreement."\n  - click "Save"\n  - in the block with newly created application click "Publish"\n\n- save `client_id` and `client_secret` in this application\n  - run\n\n  ```sh\n  art-dl --action deviantart:register\n  ```\n\n  - paste needed values\n\n- authorize application\n  - open suggested link\n  - click "Authorize"\n\nAfter that you can use it just like\n\n```sh\nart-dl -u [URL here]\n```\n\n### Proxy\n\nCreate `config.json` file with this content and fill "proxy":\n\n```json\n{\n  "proxy": "proxy-url"\n}\n```\n\nFor example, `socks5://localhost:1080`\n\n## Notes\n\n### Pixiv\n\nIf the artwork has more one image, you can specify which images should be downloaded, for example, if the artwork has 10 images and you want to download 1, 3, 4, 5 and 7 image, you can add `#1,3-5,7` to the link for that: `https://www.pixiv.net/<lang>/artworks/<id>#1,3-5,7`.\n\n### Twitter\n\nHere we use an alternative frontend for Twitter: https://nitter.net ([Github](https://github.com/zedeus/nitter))\n\n### Wallhaven\n\nNSFW images supported only with API key, to use it, get it from [account settings](https://wallhaven.cc/settings/account), then run\n\n```sh\nart-dl --action wallhaven:key\n```\n\n## Supported URL types\n\n- **artstation.com**\n  - `https://www.artstation.com/artwork/<hash>`\n  - `https://www.artstation.com/<artist>`\n- **deviantart.com**\n  - All deviations\n    - `https://www.deviantart.com/<artist>`\n    - `https://www.deviantart.com/<artist>/gallery/all`\n  - "Featured" collection\n    - `https://www.deviantart.com/<artist>/gallery`\n  - `https://www.deviantart.com/<artist>/gallery/<some number>/<gallery name>`\n  - `https://www.deviantart.com/<artist>/art/<name>`\n- **imgur.com**\n  - `https://imgur.com/a/<id>`\n  - `https://imgur.com/gallery/<id>`\n  - `https://imgur.com/t/<tag>/<id>`\n- **pixiv.net**\n  - `https://www.pixiv.net/artworks/<id>`\n  - `https://www.pixiv.net/<lang>/artworks/<id>`\n\n  - Other sites with the same content as pixiv:\n    - `https://zettai.moe/detail?id=<id>`\n- **reddit.com**\n  - `https://redd.it/<id>`\n  - `https://www.reddit.com/comments/<id>`\n  - `https://www.reddit.com/r/<subreddit>/comments/<id>/<any name>`\n- **twitter.com**\n  - `https://(mobile.)twitter.com/<account>/status/<id>`\n  - `https://nitter.net/<account>/status/<id>`\n- **wallhaven.cc**\n  - `https://wallhaven.cc/w/<id>`\n  - `https://whvn.cc/<id>`\n',
    'author': 'Ilia',
    'author_email': 'istudyatuni@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/istudyatuni/artworks-downloader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
