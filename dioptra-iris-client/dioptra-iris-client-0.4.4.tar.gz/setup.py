# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iris_client']

package_data = \
{'': ['*']}

install_requires = \
['Authlib>=0.15.5,<1.1.0', 'httpx>=0.22.0,<0.23.0']

setup_kwargs = {
    'name': 'dioptra-iris-client',
    'version': '0.4.4',
    'description': 'Python client for the Iris API.',
    'long_description': '# 🕸️ Iris Python Client\n\n[![Tests](https://img.shields.io/github/workflow/status/dioptra-io/iris-client/Tests?logo=github)](https://github.com/dioptra-io/iris-client/actions/workflows/tests.yml)\n[![Coverage](https://img.shields.io/codecov/c/github/dioptra-io/iris-client?logo=codecov&logoColor=white)](https://app.codecov.io/gh/dioptra-io/iris-client)\n[![PyPI](https://img.shields.io/pypi/v/dioptra-iris-client?logo=pypi&logoColor=white)](https://pypi.org/project/dioptra-iris-client/)\n\nMinimalist Python client for the [Iris](https://github.com/dioptra-io/iris) API,\nbuilt on top of [Authlib](https://github.com/lepture/authlib) and [httpx](https://github.com/encode/httpx).\n\n## Installation\n\n```bash\npip install dioptra-iris-client\n```\n\n## Usage\n\n```python\nfrom iris_client import IrisClient, AsyncIrisClient\n\nbase_url = "https://api.iris.dioptra.io"\nusername = "user@example.org"\npassword = "password"\n\n# Synchronous client\nwith IrisClient(base_url, username, password) as client:\n    measurements = client.get("/measurements/").json()\n\n# Asynchronous client\nasync with AsyncIrisClient(base_url, username, password) as client:\n    measurements = (await client.get("/measurements/")).json()\n\n# Helper function to fetch all the results from a paginated endpoint,\n# available for both clients:\nall_measurements = client.all("/measurements/")\n```\n\n\n### Credential provider chain\n\nThe Iris client looks for credentials in a way similar to the [AWS SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html):\n\n1. If one of `base_url`, `username` or `password` is specified, these values will be used.\n2. If none of the previous values are specified, and one of `IRIS_BASE_URL`, `IRIS_USERNAME` or `IRIS_PASSWORD`\n   environment variables are present, these values will be used.\n3. If none of the previous values are specified, and the file `~/.config/iris/credentials.json` exists,\n   the fields `base_url`, `username` and `password` will be used.\n',
    'author': 'Maxime Mouchet',
    'author_email': 'maxime.mouchet@lip6.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dioptra-io/iris-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
