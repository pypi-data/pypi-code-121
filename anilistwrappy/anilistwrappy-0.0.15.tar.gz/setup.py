# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['anilistWrapPY',
 'anilistWrapPY.Airing',
 'anilistWrapPY.Anime',
 'anilistWrapPY.Character',
 'anilistWrapPY.Manga',
 'anilistWrapPY.Media',
 'anilistWrapPY.User',
 'anilistWrapPY.errors']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.18.2,<0.19.0', 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'anilistwrappy',
    'version': '0.0.15',
    'description': 'An API Wrapper for Official Anilist.co GraphQL API',
    'long_description': '<!--\n * This file is part of anilistWrapPY (https://github.com/Dank-del/anilistWrapPY).\n * Copyright (c) 2021 Sayan Biswas, ALiwoto.\n-->\n\n# <img src="https://avatars.githubusercontent.com/u/18018524?s=200&v=4" width="35px" align="left"></img> anilistWrapPY\n\n> Name:  anilistWrapPY \\\n> Version: v0.0.15    \\\n> Edit:  23 May 2022   \\\n> By:  Dank-del (Sayan Biswas) (C) \n\n-----------------------------------------------------------\n\n![downloads](https://img.shields.io/pypi/dm/anilistWrapPY) ![ver](https://img.shields.io/pypi/v/anilistWrapPY)\n\nanilistWrapPY is an unofficial [python](https://python.org) wrapper for [anilist](https://anilist.co) API.\n\n### Table of contents\n\n- [<img src="https://avatars.githubusercontent.com/u/18018524?s=200&v=4" width="35px" align="left"></img> anilistWrapPY](#img-anilistwrappy)\n    - [Table of contents](#table-of-contents)\n  - [Supported python versions](#supported-python-versions)\n  - [Features](#features)\n  - [Getting started](#getting-started)\n  - [How to use](#how-to-use)\n    - [Airing](#airing)\n    - [Anime](#anime)\n    - [Character](#character)\n    - [Manga](#manga)\n    - [Media](#media)\n    - [User](#user)\n  - [Support and Contributions](#support-and-contributions)\n  - [Links](#links)\n  - [License](#license)\n\n<img src="https://raw.githubusercontent.com/aliwoto/aliwoto/main/resources/798246901916499998.gif" width="350px"></img>\n\n<hr/>\n\n## Supported python versions\n\nThis library, needs python 3.7 or higher version to be installed.\n\n<hr/>\n\n## Features\n\n* Uses official anilist API endpoints, which makes this library:\n  * Easy to update\n  * Guaranteed to match the docs\n  * No third party endpoints\n  * No need to serialize and deserialize data outside of library\n* It\'s in pure python, no need to install any kind of plugin or include any kind of additional files.\n* It uses GraphQL to fetch data on AniList servers. The AniList GraphQL API provides quick and powerful access to over 500k anime and manga entries, including character, staff, and live airing data.\n* Anilist Client: Using a client makes it easier to fetch every type of data you want from the servers. You only need to import client and you are ready to go!\n\n<hr/>\n\n## Getting started\n\nYou can easily download the library with the standard `pip install` command:\n\n```bash\npip install anilistWrapPY\n```\n\nYou may want to visit our pypi page [here](https://pypi.org/project/anilistwrappy/).\n\n<hr/>\n\n## How to use\n\n* <img src="https://raw.githubusercontent.com/aliwoto/aliwoto/main/resources/soulgem-homura.gif" width="15px"></img> [Airing](#Airing)\n* <img src="https://raw.githubusercontent.com/aliwoto/aliwoto/main/resources/soulgem-kyoko.gif" width="15px"></img> [Anime](#Anime)\n* <img src="https://raw.githubusercontent.com/aliwoto/aliwoto/main/resources/soulgem-madoka.gif" width="15px"></img> [Character](#Character)\n* <img src="https://raw.githubusercontent.com/aliwoto/aliwoto/main/resources/soulgem-mami.gif" width="15px"></img> [Manga](#Manga)\n* <img src="https://raw.githubusercontent.com/aliwoto/aliwoto/main/resources/soulgem-sayaka.gif" width="15px"></img> [Media](#Media)\n* <img src="https://raw.githubusercontent.com/aliwoto/aliwoto/main/resources/Yayyyyyyyyy.png" width="15px"></img> [User](#User)\n\n### Airing\n\n```py\n>>> from anilistWrapPY import aniWrapPYClient\n>>> c = aniWrapPYClient()\n>>> c.Airing("The Detective Is Already Dead")\n```\n\n### Anime\n\n```py\n>>> from anilistWrapPY import aniWrapPYClient\n>>> c = aniWrapPYClient()\n>>> c.Anime("Kanojo mo kanojo")\n```\n\n### Character\n\n```py\n>>> from anilistWrapPY import aniWrapPYClient\n>>> c = aniWrapPYClient()\n>>> c.Character("Rin tohsaka")\n```\n\n### Manga\n\n```py\n>>> from anilistWrapPY import aniWrapPYClient\n>>> c = aniWrapPYClient()\n>>> c.Manga("Classroom of the elite")\n```\n\n### Media\n\n```py\n>>> from anilistWrapPY import aniWrapPYClient\n>>> c = aniWrapPYClient()\n>>> c.Media("Talentless Nana")\n```\n\n### User\n\n```py\n>>> from anilistWrapPY import aniWrapPYClient\n>>> c = aniWrapPYClient()\n>>> c.User("mimiee")\n```\n\n<hr/>\n\n## Support and Contributions\n\n* If you think you have found a bug or have a feature request, feel free to use our [issue tracker](https://github.com/Dank-del/anilistWrapPY/issues). Before opening a new issue, please search to see if your problem has already been reported or not.  Try to be as detailed as possible in your issue reports.\n\n* If you need help using AniList APIs or have other questions about this library, we suggest you to join our [telegram community](https://t.me/chiruzon).  Please do not use the GitHub issue tracker for personal support requests.\n\n* Having a problem with library? Wanna talk with repository\'s owner? Contact the [Maintainer](https://t.me/dank_as_fuck)!\n\n* Want to have a cool multi-purpose Telegram bot in your groups? You can add [Nana[ナナ]](https://t.me/TheTalentlessBot) with full features of AniList API!\n\n<hr/>\n\n## Links\n\n* [Official website](https://anilist.co)\n* [AniList github org](https://github.com/AniList)\n* [AniList GraphQL docs](https://github.com/AniList/ApiV2-GraphQL-Docs)\n* [Support chat](https://t.me/chiruzon)\n* [Maintainer\'s Telegram](https://t.me/dank_as_fuck)\n* [Nana [ナナ]](https://t.me/TheTalentlessBot)\n\n<hr/>\n\n## License\n\n<img src="https://raw.githubusercontent.com/aliwoto/aliwoto/main/resources/Something_that_looks_like_Diamond.png" width="25px"></img> The anilistWrapPY project is under the [Unlicense](http://unlicense.org/). You can find the license file [here](LICENSE).\n',
    'author': 'Sayan Biswas',
    'author_email': 'sayan@pokurt.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Dank-del/anilistWrapPY',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
