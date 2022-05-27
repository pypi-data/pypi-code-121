# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pokesummary', 'pokesummary.data']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pokesummary = pokesummary.__main__:main']}

setup_kwargs = {
    'name': 'pokesummary',
    'version': '2.1.0',
    'description': 'An easy-to-use, informative command line interface (CLI) for accessing Pokémon summaries.',
    'long_description': '# Pokésummary\n**In the heat of a Pokémon battle,\nPokésummary lets you quickly get the information you need!**\n\nPokésummary is an easy-to-use, informative command line interface (CLI)\nfor displaying Pokémon height, weight, types, base stats, and type defenses.\nIt works completely offline, opting to use local datasets instead of APIs.\nIt requires no third-party libraries.\n\n![image](https://user-images.githubusercontent.com/29507110/113649578-adaebe00-965c-11eb-992f-7a0e2b051967.png)\n\n\n## Usage\n\n### Command-line usage\nThe simplest example is passing a Pokémon name as an argument.\nHere, we want to display Bulbasaur\'s summary,\nso we pass `bulbasaur` as an argument.\n\n    pokesummary bulbasaur\n\nMultiple Pokémon names can be chained.\nNow, we pass the names of Bulbasaur\'s whole evolution line.\nNote that Pokémon names consisting of multiple words\n(e.g. Mega Venusaur) must be surrounded by quotation marks.\n\n    pokesummary bulbasaur ivysaur venusaur "mega venusaur"\n\nIf you would like to run pokesummary interactively,\nuse the `-i` flag.\nNow we can type several Pokémon names,\nhitting Enter after each one.\nUse Ctrl-D (EOF) to exit.\n\n    pokesummary -i\n\nSince the `-i` flag reads from standard input,\nwe can pipe Pokémon names to it.\nIf we have a file `pokemon_names.txt`\nfilled with Pokémon names (each separated by newline),\nwe can use the following to display each of their summaries.\n\n    cat pokemon_names.txt | pokesummary -i\n\n### Python library usage\nStarting from version 2.0.0, you can use Pokésummary as a library.\n```pycon\n>>> from pokesummary.model import PokemonDict\n>>> pokemon_dict = PokemonDict()\n>>> my_pokemon = pokemon_dict["Lanturn"]\n>>> my_pokemon\nPokemon(name=\'Lanturn\', classification=\'Light Pokémon\', height=1.2, weight=22.5, primary_type=<PokemonType.WATER: \'Water\'>, secondary_type=<PokemonType.ELECTRIC: \'Electric\'>, base_stats=PokemonBaseStats(hp=125, attack=58, defense=58, special_attack=76, special_defense=76, speed=67))\n```\n\n## Installation\n\n### Requirements\n- Python 3.7+\n- A terminal supporting ANSI escape codes\n(most Linux and macOS terminals,\nsee [here](https://superuser.com/questions/413073/windows-console-with-ansi-colors-handling) for Windows)\n\n### Install from PyPI\n1. Install using pip\n```console\npip3 install pokesummary\n```\n\n### Install from Source Code\n1. Clone or download the repository\n2. Install using pip\n```console\npip3 install .\n```\n\n### Uninstall\n1. Uninstall using pip\n```console\npip3 uninstall pokesummary\n```\n\n## Contributing\nPlease see [CONTRIBUTING.md](./CONTRIBUTING.md).\n\n## Acknowledgements\n- Type chart from [Pokémon Database](https://pokemondb.net/type)\n- Pokémon data from [Yu-Chi Chiang\'s fixed database](https://www.kaggle.com/mrdew25/pokemon-database/discussion/165031)\n',
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
