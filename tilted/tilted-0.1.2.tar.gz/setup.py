# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tilted']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tilted',
    'version': '0.1.2',
    'description': 'Tilted is a lightweight, open-source Python package with a simple interface for poker hand evaluation & comparison.',
    'long_description': '\n# Tilted\n<img align="left" src="https://user-images.githubusercontent.com/8881202/169894189-c4d64c08-7751-4d0e-a95f-640f07c2e7bd.jpeg" width="100" height="100" />\n\nTilted is a lightweight, open-source Python package with a simple interface for poker hand evaluation & comparison.\n\n<img src="https://img.shields.io/github/v/release/MaxAtkinson/tilted" />\n\n<br />\n<br />\n\n## Installation\nWith Poetry:\n```sh\npoetry add tilted\n```\n\nWith Pip:\n```sh\npip install tilted\n```\n\n## Basic Usage\nTilted can be used to generate, evaluate and compare 5-card poker hands.\n\n### Hand Generation\nTo generate a random hand:\n```python\nfrom tilted import Deck, Hand\n\n\ndeck = Deck()\nunknown_hand = Hand(deck.draw_many(5))\n\nunknown_hand  # <Hand: 8♦ T♠ T♣ Q♣ K♥>\nunknown_hand.hand_rank  # <HandRank.PAIR: 2>\n```\n\n### Hand Evaluation\nTo evaluate an unknown hand:\n```python\nfrom tilted import Card, CardRank, CardSuit, Hand\n\n\nunknown_hand = Hand([\n  Card(CardRank.TEN, CardSuit.SPADES),\n  Card(CardRank.JACK, CardSuit.SPADES),\n  Card(CardRank.QUEEN, CardSuit.SPADES),\n  Card(CardRank.KING, CardSuit.SPADES),\n  Card(CardRank.ACE, CardSuit.SPADES),\n])\n\nunknown_hand.hand_rank  # <HandRank.ROYAL_FLUSH: 10>\n```\n\n### Hand Comparison\nTo compare two hands:\n```python\nfrom tilted import Card, CardRank, CardSuit, Hand\n\n\nroyal_flush = Hand([\n  Card(CardRank.TEN, CardSuit.SPADES),\n  Card(CardRank.JACK, CardSuit.SPADES),\n  Card(CardRank.QUEEN, CardSuit.SPADES),\n  Card(CardRank.KING, CardSuit.SPADES),\n  Card(CardRank.ACE, CardSuit.SPADES),\n])\n\nstraight_flush = Hand([\n  Card(CardRank.NINE, CardSuit.HEARTS),\n  Card(CardRank.TEN, CardSuit.HEARTS),\n  Card(CardRank.JACK, CardSuit.HEARTS),\n  Card(CardRank.QUEEN, CardSuit.HEARTS),\n  Card(CardRank.KING, CardSuit.HEARTS),\n])\n\nroyal_flush > straight_flush  # True\n```\n\n\n## Roadmap\n\n### Features\n- [x] Hand evaluation\n- [x] Hand comparison\n- [x] Deck support\n- [ ] Board & dealing (Flop, Turn, River)\n- [ ] Full board & hole card evaluation\n- [ ] Expand beyond Texas Hold \'Em (Pot Limit Omaha)\n\n### Deployment\n- [ ] CI\n',
    'author': 'Max Atkinson',
    'author_email': 'hiremaxatkinson@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MaxAtkinson/tilted',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
