# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dipdup',
 'dipdup.datasources',
 'dipdup.datasources.coinbase',
 'dipdup.datasources.ipfs',
 'dipdup.datasources.metadata',
 'dipdup.datasources.tzkt',
 'dipdup.utils']

package_data = \
{'': ['*'], 'dipdup': ['configs/*', 'sql/on_reindex/*', 'templates/*']}

install_requires = \
['APScheduler>=3.8.0,<4.0.0',
 'aiohttp>=3.8.0,<4.0.0',
 'aiolimiter>=1.0.0-beta.1,<2.0.0',
 'anyio>=3.3.2,<4.0.0',
 'asyncclick>=8.0.1,<9.0.0',
 'asyncpg>=0.24.0,<0.25.0',
 'datamodel-code-generator>=0.11.18,<0.12.0',
 'fcache>=0.4.7,<0.5.0',
 'orjson>=3.6.6,<4.0.0',
 'prometheus-client>=0.12.0,<0.13.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyhumps>=3.0.2,<4.0.0',
 'pysignalr>=0.1.2,<0.2.0',
 'python-dotenv>=0.19.0,<0.20.0',
 'ruamel.yaml>=0.17.2,<0.18.0',
 'sentry-sdk>=1.4.3,<2.0.0',
 'sqlparse>=0.4.2,<0.5.0',
 'tabulate>=0.8.9,<0.9.0',
 'tortoise-orm==0.19.1',
 'typing-inspect>=0.6.0,<0.7.0']

extras_require = \
{'pytezos': ['pytezos>=3.2.4,<4.0.0']}

entry_points = \
{'console_scripts': ['dipdup = dipdup.cli:cli']}

setup_kwargs = {
    'name': 'dipdup',
    'version': '5.1.2',
    'description': 'Python SDK for developing indexers of Tezos smart contracts inspired by The Graph',
    'long_description': '___\n\n<center> ✨ We invite you to take part in the <a href="https://forms.gle/nMkQnmukRPmwQedLA">DipDup Community Survey April 2022</a>! ✨ </center>\n\n___\n\n[![Python](https://img.shields.io/badge/made%20with-python-blue.svg?)](https://www.python.org)\n[![GitHub stars](https://img.shields.io/github/stars/dipdup-net/dipdup-py)](https://github.com/dipdup-net/dipdup-py)\n[![Latest stable release](https://img.shields.io/github/v/release/dipdup-net/dipdup-py?label=stable)](https://github.com/dipdup-net/dipdup-py/releases)\n[![Latest pre-release)](https://img.shields.io/github/v/release/dipdup-net/dipdup-py?include_prereleases&label=latest)](https://github.com/dipdup-net/dipdup-py/releases)\n[![PyPI monthly downloads](https://img.shields.io/pypi/dm/dipdup)](https://pypi.org/project/dipdup/)\n<br>\n[![GitHub tests](https://img.shields.io/github/workflow/status/dipdup-net/dipdup-py/Test)](https://github.com/dipdup-net/dipdup-py/actions)\n[![GitHub issues](https://img.shields.io/github/issues/dipdup-net/dipdup-py)](https://github.com/dipdup-net/dipdup-py/issues)\n[![GitHub pull requests](https://img.shields.io/github/issues-pr/dipdup-net/dipdup-py)](https://github.com/dipdup-net/dipdup-py/pulls)\n[![License: MIT](https://img.shields.io/github/license/dipdup-net/dipdup-py)](https://github.com/dipdup-net/dipdup-py/blob/master/LICENSE)\n\n```text\n        ____   _         ____              \n       / __ \\ (_)____   / __ \\ __  __ ____ \n      / / / // // __ \\ / / / // / / // __ \\\n     / /_/ // // /_/ // /_/ // /_/ // /_/ /\n    /_____//_// .___//_____/ \\__,_// .___/ \n             /_/                  /_/      \n```\n\nDipDup is a Python framework for building indexers of [Tezos](https://tezos.com/) smart-contracts. It helps developers focus on the business logic instead of writing data storing and serving boilerplate. DipDup-based indexers are selective, which means only required data is requested. This approach allows to achieve faster indexing times and decreased load on APIs DipDup uses.\n\n* **Ready to build your first indexer?** Head to [Quickstart](https://docs.dipdup.net/quickstart).\n\n* **Looking for examples?** Check out [Demo Projects](https://github.com/dipdup-net/dipdup-py/tree/master/src).\n\n* **Want to contribute?** See [Contribution Guide](https://github.com/dipdup-net/dipdup-py/tree/master/CONTRIBUTING.md).\n\n* **Have a question?** Contact us at [Discord](https://discord.gg/JZKhv7uW), [Telegram](https://t.me/baking_bad_chat) or [Slack](https://tezos-dev.slack.com/archives/CV5NX7F2L)!\n\n\nThis project is maintained by [Baking Bad](https://baking-bad.org/) team.  \nDevelopment is supported by [Tezos Foundation](https://tezos.foundation/).\n',
    'author': 'Lev Gorodetskiy',
    'author_email': 'github@droserasprout.space',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://dipdup.net/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
