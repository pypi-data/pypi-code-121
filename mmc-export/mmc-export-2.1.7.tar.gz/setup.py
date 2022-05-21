# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mmc_export', 'mmc_export.Formats', 'mmc_export.Helpers']

package_data = \
{'': ['*']}

install_requires = \
['Werkzeug>=2.1.2,<3.0.0',
 'aiohttp-client-cache[filesystem,sqlite]>=0.6.1,<0.7.0',
 'aiohttp>=3.8.1,<4.0.0',
 'cryptography>=37.0.2,<38.0.0',
 'jsonpickle>=2.1.0,<3.0.0',
 'murmurhash2>=0.2.10,<0.3.0',
 'pytoml>=0.1.21,<0.2.0',
 'tenacity>=8.0.1,<9.0.0',
 'tomli>=2.0.1,<3.0.0',
 'xxhash>=3.0.0,<4.0.0']

entry_points = \
{'console_scripts': ['mmc-export = mmc_export:main']}

setup_kwargs = {
    'name': 'mmc-export',
    'version': '2.1.7',
    'description': 'Export MMC modpack to other modpack formats',
    'long_description': "# MultiMC advanced exporter\n![PyPI pyversions](https://img.shields.io/pypi/pyversions/mmc-export)\n[![PyPI version](https://img.shields.io/pypi/v/mmc-export?label=mmc-export&color=%2347a637)](https://pypi.org/project/mmc-export)\n![PyPI downloads](https://img.shields.io/pypi/dm/mmc-export?color=%23894bbf)\n[![GitHub license](https://img.shields.io/github/license/RozeFound/mmc-export)](/LICENSE)\n\nSince MultiMC export features are very limited, I created a script that solves this problem, with this script you can export MultiMC pack to any popular format (e.g. curseforge, modrinth, packwiz). MultiMC forks which didn't changed export format much also supported, PolyMC support approved.\n\n# Features\n\n- Support conversion to:\n    - CurseForge\n    - Modrinth\n    - packwiz\n- Detects downloadable resourcepacks and shaders\n- Supports github parsing[¹](#github-rate-limits)\n- Loose modrinth search\n- User friendly toml config\n- Multiple output formats at once\n\n---\n### Github rate limits\n\nGithub has limited requests per hour (up to 60), this means that if you have more than 60 mods, the rest will be excluded from github search.\n\nTo solve this, you can authorize in application. \\\nYou need to create personal key [here](https://github.com/settings/tokens) (with no permissions), and pass it as argument to script along with your username, like:\n```\nmmc-export -i modpack -f format --github-auth username:token\n```\nI recommend you to store tokens in enviroment variables for security reasons.\n\n# How to Use\n```\nmmc-export -i modpack.zip -c config.toml -f Modrinth packwiz -o converted_modpacks\n```\nIt's recommended to fill config at least with basic info like name and version, some launchers can fail import if these values are empty.\n## Syntax:\n```\nmmc-export [-h] [-c CONFIG] -i INPUT -f FORMAT [-o OUTPUT] [--github-auth GITHUB_AUTH] [--modrinth-search SEARCH_TYPE] [--exclude-providers PROVIDERS] [--exclude-forbidden]\n```\n\n### Explanation:\n\n```\n-h --help: prints help\n-i --input: path to modpack, must be zip file exported from MultiMC.\n-c --config: path to config, used to fill the gaps like description or losted mods.\n-f --format: output formats, must be separated by spaces.\n-o --output: directory where converted zip files will be stored.\n--github-auth: Github Auth in format username:token\n--modrinth-search: modrinth search accuracy (exact (default), accurate, loose)\n--exclude-providers: providers you wish to exclude from search (cf, mr, gh)\n--exclude-forbidden: set to not ignore CF distribution flag. Must be enabled for public modpacks.\n```\n\nAvaliable formats:     - `CurseForge, Modrinth, packwiz, Intermediate` (case-sensitive)\n\n`Intermediate` must be used for debugging only, as it may contain sensitive information like username.\n\n# How to Install / Update\n```\npip install -U mmc-export\n```\n",
    'author': 'RozeFound',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/RozeFound/mmc-export',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
