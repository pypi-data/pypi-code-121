# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mtg_parser']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'pyparsing>=2.4.7,<3.0.0',
 'requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'mtg-parser',
    'version': '0.0.1a24',
    'description': 'Magic: the Gathering decklist parser',
    'long_description': '# mtg-parser\n\n![PyPI](https://img.shields.io/pypi/v/mtg-parser)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mtg-parser)\n![GitHub](https://img.shields.io/github/license/lheyberger/mtg-parser)\n\n## How to install\n\n\tpip install mtg-parser\n\n\n## Quick Start\n\n`mtg_parser.parse_deck()` can parse any decklist (textual or online) but if for any reason you want the specialized version, here are the supported websites:\n* aetherhub.com\n* archidekt.com\n* deckstats.net\n* moxfield.com\n* mtggoldfish.com\n* scryfall.com\n* tappedout.net\n* tcgplayer.com\n\n\n### From textual decklist\n\n`mtg_parser` can parse textual decklists with either MTGO or MTGA format\n\n\timport mtg_parser\n\t\n\tdecklist = """\n\t\t1 Atraxa, Praetors\' Voice\n\t\t1 Imperial Seal\n\t\t1 Lim-Dûl\'s Vault\n\t\t1 Jeweled Lotus (CMR) 319\n\t\t1 Llanowar Elves (M12) 182\n\t\t3 Brainstorm #Card Advantage #Draw\n\t"""\n\t\n\tcards = mtg_parser.decklist.parse_deck(decklist)\n\t\n\tfor card in cards:\n\t\tprint(card)\n\n### From aetherhub.com\n\n`mtg_parser` can parse public decks from aetherhub.com\n\n\timport mtg_parser\n\t\n\turl = \'https://aetherhub.com/Deck/<deckname>\'\n\tcards = mtg_parser.aetherhub.parse_deck(url)\n\tfor card in cards:\n\t\tprint(card)\n\n\n### From archidekt.com\n\n`mtg_parser` can parse public decks from archidekt.com\n\n\timport mtg_parser\n\t\n\turl = \'https://www.archidekt.com/decks/<deckid>/\'\n\tcards = mtg_parser.archidekt.parse_deck(url)\n\tfor card in cards:\n\t\tprint(card)\n\n\n### From deckstats.net\n\n`mtg_parser` can parse public decks from deckstats.net\n\n\timport mtg_parser\n\t\n\turl = \'https://deckstats.net/decks/<userid>/<deckid>\'\n\tcards = mtg_parser.deckstats.parse_deck(url)\n\tfor card in cards:\n\t\tprint(card)\n\n\n### From moxfield.com\n\n`mtg_parser` can parse public decks from moxfield.com\n\n\timport mtg_parser\n\t\n\turl = \'https://www.moxfield.com/decks/<deckid>\'\n\tcards = mtg_parser.moxfield.parse_deck(url)\n\tfor card in cards:\n\t\tprint(card)\n\n\n### From mtggoldfish.com\n\n`mtg_parser` can parse public decks from mtggoldfish.com\n\n\timport mtg_parser\n\t\n\turl = \'https://www.mtggoldfish.com/deck/<deckid>\'\n\tcards = mtg_parser.mtggoldfish.parse_deck(url)\n\tfor card in cards:\n\t\tprint(card)\n\n\n### From scryfall.com\n\n`mtg_parser` can parse public decks from scryfall.com\n\n\timport mtg_parser\n\t\n\turl = \'https://scryfall.com/<userid>/decks/<deckid>/\'\n\tcards = mtg_parser.scryfall.parse_deck(url)\n\tfor card in cards:\n\t\tprint(card)\n\n\n### From tappedout.net\n\n`mtg_parser` can parse public decks from tappedout.net\n\n\timport mtg_parser\n\t\n\turl = \'https://tappedout.net/mtg-decks/<deckid>/\'\n\tcards = mtg_parser.tappedout.parse_deck(url)\n\tfor card in cards:\n\t\tprint(card)\n\n\n### From tcgplayer.com\n\n`mtg_parser` can parse public decks from tcgplayer.com\n\n\timport mtg_parser\n\t\n\turl = \'https://decks.tcgplayer.com/magic/<deckpath>\'\n\tcards = mtg_parser.tcgplayer.parse_deck(url)\n\tfor card in cards:\n\t\tprint(card)\n',
    'author': 'Ludovic Heyberger',
    'author_email': '940408+lheyberger@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lheyberger/mtg-parser',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
