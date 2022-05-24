# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pysignalr', 'pysignalr.protocol', 'pysignalr.transport']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'msgpack>=1.0.2,<2.0.0', 'websockets==10.3']

setup_kwargs = {
    'name': 'pysignalr',
    'version': '0.1.2',
    'description': 'Modern, reliable and async-ready client for SignalR protocol',
    'long_description': "# pysignalr\n[![Pypi](https://img.shields.io/pypi/v/pysignalr.svg)](https://pypi.org/project/pysignalr/)\n\n**pysignalr** is a modern, reliable and async-ready client for [SignalR protocol](https://docs.microsoft.com/en-us/aspnet/core/signalr/introduction?view=aspnetcore-5.0). This project started as an asyncio fork of mandrewcito's [signalrcore](https://github.com/mandrewcito/signalrcore) library.\n\n## Usage\n\nLet's connect to [TzKT](https://tzkt.io/), indexer and explorer of Tezos blockchain, and subscribe to all operations:\n\n```python\nimport asyncio\nfrom contextlib import suppress\nfrom typing import Any, Dict, List\nfrom pysignalr.client import SignalRClient\nfrom pysignalr.messages import CompletionMessage\n\n\nasync def on_open() -> None:\n    print('Connected to the server')\n\n\nasync def on_close() -> None:\n    print('Disconnected from the server')\n\n\nasync def on_message(message: List[Dict[str, Any]]) -> None:\n    print(f'Received message: {message}')\n\n\nasync def on_error(message: CompletionMessage) -> None:\n    print(f'Received error: {message.error}')\n\n\nasync def main():\n    client = SignalRClient('https://api.tzkt.io/v1/events')\n\n    client.on_open(on_open)\n    client.on_close(on_close)\n    client.on_error(on_error)\n    client.on('operations', on_message)\n\n    await asyncio.gather(\n        client.run(),\n        client.send('SubscribeToOperations', [{}]),\n    )\n\n\nwith suppress(KeyboardInterrupt, asyncio.CancelledError):\n    asyncio.run(main())\n```\n\n## Roadmap to the stable release\n\n- [ ] More documentation, both internal and user.\n- [ ] Integration tests with containerized ASP hello-world server.\n- [ ] Ensure that authentication works correctly.\n",
    'author': 'Lev Gorodetskiy',
    'author_email': 'github@droserasprout.space',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dipdup-net/pysignalr',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
