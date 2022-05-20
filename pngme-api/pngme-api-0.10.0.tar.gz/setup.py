# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['api', 'api.resources']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.22.0,<0.23.0',
 'nest-asyncio>=1.5.4,<2.0.0',
 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'pngme-api',
    'version': '0.10.0',
    'description': "API client used to access Pngme's financial data APIs.",
    'long_description': '<p align="center">\n  <img src="https://admin.pngme.com/logo.png" alt="Pngme" width="100" height="100">\n</p>\n\n<h3 align="center">Python API Client</h3>\n\nThis package exposes a synchronous and asynchronous client used to interact with Pngme\'s financial data APIs.\n\n## Install\n\nInstall the latest version with:\n\n```bash\npip3 install pngme-api\n```\n\n## Quick start\n\nCreate a `Client` instance using your API `token` found in the [Pngme Dashboard](https://admin.pngme.com):\n\n```python\nfrom pngme.api import Client\n\ntoken = "" # your API token\nclient = Client(token)\n```\n\n> If you\'re using [`asyncio`](https://docs.python.org/3/library/asyncio.html), you can import and use the `AsyncClient` instead. See [using with asyncio](#using-with-asyncio).\n\nWe can list or search the available [`/users`](https://developers.api.pngme.com/reference/get_users):\n\n```python\nusers = client.users.get()\nusers = client.users.get(search="2343456789012")\n```\n\nFor a user of interest, we can get a list of the user\'s [`/institutions`](https://developers.api.pngme.com/reference/get_users-user-uuid-institutions):\n\n```python\nuser_uuid = "33b6215d-3d75-4271-801c-6da27603a8be"\n\ninstitutions = client.institutions.get(user_uuid=user_uuid)\n```\n\nThen for a given institution, we can get a list of the user\'s [`/transactions`](https://developers.api.pngme.com/reference/get_users-user-uuid-institutions-institution-id-transactions), [`/balances`](https://developers.api.pngme.com/reference/get_users-user-uuid-institutions-institution-id-balances), or [`/alerts`](https://developers.api.pngme.com/reference/get_users-user-uuid-institutions-institution-id-alerts):\n\n```python\nuser_uuid = "33b6215d-3d75-4271-801c-6da27603a8be"\ninstitution_id = "zenithbank"\n\ntransactions = client.transactions.get(user_uuid=user_uuid, institution_id=institution_id)\nbalances = client.balances.get(user_uuid=user_uuid, institution_id=institution_id)\nalerts = client.alerts.get(user_uuid=user_uuid, institution_id=institution_id)\n```\n\n## asyncio\n\nWe can make multiple requests concurrently using `asyncio` by creating a `Client` instance with your API `token` found in the [Pngme Dashboard](https://admin.pngme.com):\n\n```python\nfrom pngme.api import AsyncClient\n\ntoken = "" # your API token\nclient = AsyncClient(token)\n```\n\nSimilar to the synchronous `Client`, we can list or search the available [`/users`](https://developers.api.pngme.com/reference/get_users):\n\n```python\nasync def get_users(client: AsyncClient):\n    users = await client.users.get()\n    return users\n\nusers = asyncio.run(get_users(client))\n```\n\nThis is helpful to concurrently execute multiple requests, such as fetching a user\'s transaction history across all accounts by iterating over institutions associated with a user:\n\n```python\nasync def get_transactions(client: AsyncClient, user_uuid: str):\n    # Find institutions where the user has one or more accounts\n    institutions = await client.institutions.get(user_uuid)\n\n    # Concurrently fetch transactions for all institutions\n    institution_ids = [institution.institution_id for institution in institutions]\n    coroutines = [\n        client.transactions.get(user_uuid, institution_id)\n        for institution_id in institution_ids\n    ]\n    transactions = await asyncio.gather(*coroutines)\n\n    # Associate transactions with the relevant institution_id\n    return dict(zip(institution_ids, transactions))\n\nuser_uuid = "33b6215d-3d75-4271-801c-6da27603a8be"\ntransactions = asyncio.run(get_transactions(client, user_uuid))\n```\n\n## Next steps\n\n* Browse the Pngme [Feature Library](https://github.com/pngme/pngme-feature-library) to see how data scientists integrate our APIs into decisioning workflows\n* Explore the definitions of each response field in the [API Docs](https://developers.api.pngme.com/reference/getting-started-with-your-api)\n',
    'author': 'Ben Fasoli',
    'author_email': 'ben@pngme.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://developers.api.pngme.com/reference/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
