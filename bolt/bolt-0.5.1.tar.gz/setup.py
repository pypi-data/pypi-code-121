# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bolt', 'bolt.contrib', 'bolt.resources']

package_data = \
{'': ['*']}

install_requires = \
['beet>=0.64.0', 'mecha>=0.49.1']

setup_kwargs = {
    'name': 'bolt',
    'version': '0.5.1',
    'description': 'Supercharge Minecraft commands with Python',
    'long_description': '# Bolt\n\n[![GitHub Actions](https://github.com/mcbeet/bolt/workflows/CI/badge.svg)](https://github.com/mcbeet/bolt/actions)\n[![PyPI](https://img.shields.io/pypi/v/bolt.svg)](https://pypi.org/project/bolt/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bolt.svg)](https://pypi.org/project/bolt/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Discord](https://img.shields.io/discord/900530660677156924?color=7289DA&label=discord&logo=discord&logoColor=fff)](https://discord.gg/98MdSGMm8j)\n\n> Supercharge Minecraft commands with Python.\n\n```python\ninfinite_invisibility = {\n    Id: 14,\n    Duration: 999999,\n    Amplifier: 1,\n    ShowParticles: false,\n}\n\ndef summon_chicken_army(n):\n    for i in range(n):\n        summon chicken ~i ~ ~ {\n            Tags: [f"quack{i}"],\n            IsChickenJockey: true,\n            Passengers: [{\n                id: zombie,\n                IsBaby: true,\n                ActiveEffects: [infinite_invisibility]\n            }]\n        }\n\nsay Go forth, my minions!\nsummon_chicken_army(16)\n```\n\n## Installation\n\nThe package can be installed with `pip`.\n\n```bash\n$ pip install bolt\n```\n\n## Contributing\n\nContributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`poetry`](https://python-poetry.org/).\n\n```bash\n$ poetry install\n```\n\nYou can run the tests with `poetry run pytest`.\n\n```bash\n$ poetry run pytest\n```\n\nThe project must type-check with [`pyright`](https://github.com/microsoft/pyright). If you\'re using VSCode the [`pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension should report diagnostics automatically. You can also install the type-checker locally with `npm install` and run it from the command-line.\n\n```bash\n$ npm run watch\n$ npm run check\n```\n\nThe code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).\n\n```bash\n$ poetry run isort bolt tests\n$ poetry run black bolt tests\n$ poetry run black --check bolt tests\n```\n\n---\n\nLicense - [MIT](https://github.com/mcbeet/bolt/blob/main/LICENSE)\n',
    'author': 'Valentin Berlier',
    'author_email': 'berlier.v@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mcbeet/bolt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
