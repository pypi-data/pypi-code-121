# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['botbase', 'botbase.coggies', 'botbase.wraps']

package_data = \
{'': ['*']}

install_requires = \
['asyncpg>=0.25.0',
 'jishaku==2.4.0',
 'nextcord-ext-menus>=1.5.2,<2.0.0',
 'nextcord>=2.0.0-alpha.10',
 'psutil>=5.9.0,<6.0.0']

entry_points = \
{'console_scripts': ['botbase = botbase.cli:main']}

setup_kwargs = {
    'name': 'ooliver-botbase',
    'version': '1.14.7',
    'description': 'A personal nextcord bot base package for bots.',
    'long_description': '# I\'m Sorry\n\nI wish you luck in trying to use this.\nFuture me or anyone\n\n## Oh yeah the config\n\ndb_enabled: bool default True\n\ndb_url: str either this or name\n\ndb_name: str either this or url\n\ndb_user: str default "ooliver"\n\ndb_host str default "localhost"\n\nversion: str default "0.0.0"\n\naiohttp_enabled: bool default True\n\ncolors: list[int] default [0x9966CC]\n\nblacklist_enabled: bool default True\n\nprefix: str | list[str]\n\nhelpmsg: str default defaulthelpmsg\n\nhelpindex: str default defaulthelpindex\n\nhelptitle: str default "Help Me!"\n\nhelpfields: dict[str, str] default {}\n\nhelpinsert: str default ""\n\nemojiset: Emojis[str, str] default Emojis()\n\nlogchannel: int default None\n\nguild_ids list[int] default None\n',
    'author': 'ooliver1',
    'author_email': 'oliverwilkes2006@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ooliver1/botbase',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
