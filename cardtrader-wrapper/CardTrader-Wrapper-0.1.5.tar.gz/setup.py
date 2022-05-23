# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cardtrader', 'cardtrader.schemas']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses-json>=0.5.7,<0.6.0',
 'ratelimit>=2.2.1,<3.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'cardtrader-wrapper',
    'version': '0.1.5',
    'description': 'A Python wrapper for the CardTrader API.',
    'long_description': '# CardTrader Wrapper\n\n[![PyPI - Python](https://img.shields.io/pypi/pyversions/CardTrader-Wrapper.svg?logo=PyPI&label=Python&style=flat-square)](https://pypi.python.org/pypi/CardTrader-Wrapper/)\n[![PyPI - Status](https://img.shields.io/pypi/status/CardTrader-Wrapper.svg?logo=PyPI&label=Status&style=flat-square)](https://pypi.python.org/pypi/CardTrader-Wrapper/)\n[![PyPI - Version](https://img.shields.io/pypi/v/CardTrader-Wrapper.svg?logo=PyPI&label=Version&style=flat-square)](https://pypi.python.org/pypi/CardTrader-Wrapper/)\n[![PyPI - License](https://img.shields.io/pypi/l/CardTrader-Wrapper.svg?logo=PyPI&label=License&style=flat-square)](https://opensource.org/licenses/GPL-3.0)\n\n[![Black](https://img.shields.io/badge/Black-Enabled-000000?style=flat-square)](https://github.com/psf/black)\n[![Flake8](https://img.shields.io/badge/Flake8-Enabled-informational?style=flat-square)](https://github.com/PyCQA/flake8)\n[![Pre-Commit](https://img.shields.io/badge/Pre--Commit-Enabled-informational?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)\n\n[![Github - Contributors](https://img.shields.io/github/contributors/Buried-In-Code/CardTrader-Wrapper.svg?logo=Github&label=Contributors&style=flat-square)](https://github.com/Buried-In-Code/CardTrader-Wrapper/graphs/contributors)\n\n[![Github Action - Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/CardTrader-Wrapper/Code%20Analysis?logo=Github-Actions&label=Code-Analysis&style=flat-square)](https://github.com/Buried-In-Code/CardTrader-Wrapper/actions/workflows/code-analysis.yaml)\n[![Github Action - Testing](https://img.shields.io/github/workflow/status/Buried-In-Code/CardTrader-Wrapper/Testing?logo=Github-Actions&label=Tests&style=flat-square)](https://github.com/Buried-In-Code/CardTrader-Wrapper/actions/workflows/testing.yaml)\n\nA [Python](https://www.python.org/) wrapper for the [CardTrader](https://cardtrader.com) API.\n\n## Installation\n\n### Poetry\n\n```bash\n$ poetry add CardTrader-Wrapper\n```\n\n### Local Setup\n\n1. Fork this repo\n2. Create the env variable `CARDTRADER_ACCESS_TOKEN` with your access token from [CardTrader](https://cardtrader.com).\n3. Make sure you have [Python](https://python.org/) installed: `python --version`\n4. Make sure you have [Poetry](https://python-poetry.org/) installed: `poetry --version`\n5. Clone the repo: `git clone https://github.com/<Username>/CardTrader-Wrapper`\n6. Install the project and its dependencies via poetry: `poetry install`\n\n## Example Usage\n\n```python\nfrom cardtrader.service import CardTrader\nfrom cardtrader.sqlite_cache import SQLiteCache\n\nsession = CardTrader(access_token="Access Token", cache=SQLiteCache())\n\n# List Games\nresults = session.games()\nfor game in results:\n    print(f"{game.id_} | {game.display_name}")\n\n# List Magic: the Gathering Expansions\nresults = [x for x in session.expansions() if x.game_id == 1]\nfor expansion in results:\n    print(f"{expansion.id_} | {expansion.code} - {expansion.name}")\n\n# List Magic: the Gathering - Game Night Cards for sale\nblueprints = session.blueprints(expansion_id=1)\nfor card_blueprint in blueprints:\n    products = session.products_by_blueprint(blueprint_id=card_blueprint.id_)\n    for product in products:\n        print(f"{product.price.formatted} | {card_blueprint.name}")\n```\n\n## Socials\n\n[![Social - Discord](https://img.shields.io/badge/Discord-The--DEV--Environment-7289DA?logo=Discord&style=flat-square)](https://discord.gg/nqGMeGg)\n',
    'author': 'Buried-In-Code',
    'author_email': 'BuriedInCode@tuta.io',
    'maintainer': 'Buried-In-Code',
    'maintainer_email': 'BuriedInCode@tuta.io',
    'url': 'https://github.com/Buried-In-Code/CardTrader-Wrapper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
