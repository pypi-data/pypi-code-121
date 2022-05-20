# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pokesummary', 'pokesummary.data']

package_data = \
{'': ['*'],
 'pokesummary': ['.mypy_cache/*',
                 '.mypy_cache/3.9/*',
                 '.mypy_cache/3.9/_typeshed/*',
                 '.mypy_cache/3.9/collections/*',
                 '.mypy_cache/3.9/ctypes/*',
                 '.mypy_cache/3.9/email/*',
                 '.mypy_cache/3.9/importlib/*',
                 '.mypy_cache/3.9/importlib/metadata/*',
                 '.mypy_cache/3.9/json/*',
                 '.mypy_cache/3.9/os/*',
                 '.mypy_cache/3.9/pokesummary/*',
                 '.mypy_cache/3.9/pokesummary/data/*'],
 'pokesummary.data': ['.mypy_cache/*',
                      '.mypy_cache/3.9/*',
                      '.mypy_cache/3.9/_typeshed/*',
                      '.mypy_cache/3.9/collections/*',
                      '.mypy_cache/3.9/ctypes/*',
                      '.mypy_cache/3.9/email/*',
                      '.mypy_cache/3.9/importlib/*',
                      '.mypy_cache/3.9/importlib/metadata/*',
                      '.mypy_cache/3.9/os/*',
                      '.mypy_cache/3.9/pokesummary/*',
                      '.mypy_cache/3.9/pokesummary/data/*']}

entry_points = \
{'console_scripts': ['pokesummary = pokesummary.__main__:main']}

setup_kwargs = {
    'name': 'pokesummary',
    'version': '2.0.0',
    'description': 'An easy-to-use, informative command line interface (CLI) for accessing Pokémon summaries.',
    'long_description': '# Pokésummary\n**In the heat of a Pokémon battle,\nPokésummary lets you quickly get the information you need!**\n\nPokésummary is an easy-to-use, informative command line interface (CLI)\nfor displaying Pokémon height, weight, types, base stats, and type defenses.\nIt works completely offline, opting to use local datasets instead of APIs.\nIt requires no third-party libraries.\n\n![image](https://user-images.githubusercontent.com/29507110/113649578-adaebe00-965c-11eb-992f-7a0e2b051967.png)\n\n\n## Usage\n\n### Command-line usage\n```console\nusage: pokesummary [-h] [-i] [-s] [-v] [pokemon_names ...]\n\nGet summaries for a Pokémon or multiple Pokémon.\n\npositional arguments:\n  pokemon_names        the Pokémon to look up\n\noptional arguments:\n  -h, --help           show this help message and exit\n  -i, --interactive    run interactively\n  -s, --show-examples  show example uses of the program\n  -v, --version        show program\'s version number and exit\n```\n\n### Python library usage\nStarting from version 2.0.0, you can use Pokésummary as a library.\nNote that the API is subject to change.\n```pycon\n>>> from pokesummary.model import PokemonDict\n>>> pokemon_data = PokemonDict().data\n>>> my_pokemon = pokemon_data["Lanturn"]\n>>> my_pokemon.base_stats.special_attack\n76\n>>> my_pokemon.primary_type\n<PokemonType.WATER: \'Water\'>\n```\n\n## Installation\n\n### Requirements\n- Python 3.7+\n- A terminal supporting ANSI escape codes\n(most Linux and macOS terminals,\nsee [here](https://superuser.com/questions/413073/windows-console-with-ansi-colors-handling) for Windows)\n\n### Install from PyPI\n1. Install using pip\n```console\npip3 install pokesummary\n```\n\n### Install from Source Code\n1. Clone or download the repository\n2. Install using pip\n```console\npip3 install .\n```\n\n### Uninstall\n1. Uninstall using pip\n```console\npip3 uninstall pokesummary\n```\n\n## Contributing\nPlease see [CONTRIBUTING.md](./CONTRIBUTING.md).\n\n## Acknowledgements\n- Type chart from [Pokémon Database](https://pokemondb.net/type)\n- Pokémon data from [Yu-Chi Chiang\'s fixed database](https://www.kaggle.com/mrdew25/pokemon-database/discussion/165031)\n',
    'author': 'Fisher Sun',
    'author_email': 'fisher521.fs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tactlessfish/pokesummary',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
