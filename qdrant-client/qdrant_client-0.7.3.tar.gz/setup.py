# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qdrant_client',
 'qdrant_client.conversions',
 'qdrant_client.grpc',
 'qdrant_client.http',
 'qdrant_client.http.api',
 'qdrant_client.http.models',
 'qdrant_client.uploader',
 'qdrant_openapi_client',
 'qdrant_openapi_client.api',
 'qdrant_openapi_client.models']

package_data = \
{'': ['*']}

install_requires = \
['betterproto==2.0.0b4',
 'grpcio>=1.46.0,<2.0.0',
 'httpx>=0.22.0,<0.23.0',
 'loguru>=0.5.3,<0.6.0',
 'numpy>=1.21,<2.0',
 'pydantic>=1.8,<2.0',
 'tqdm>=4.56.0,<5.0.0',
 'typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'qdrant-client',
    'version': '0.7.3',
    'description': 'Client library for the Qdrant vector search engine',
    'long_description': '# Python Qdrant client library \n\nClient library for the [Qdrant](https://github.com/qdrant/qdrant) vector search engine.\n\nLibrary contains type definitions for all Qdrant API and allows to make both Sync and Async requests.\n\n`Pydantic` is used for describing request models and `httpx` for handling http queries.\n\nClient allows calls for all [Qdrant API methods](https://qdrant.github.io/qdrant/redoc/index.html) directly.\nIt also provides some additional helper methods for frequently required operations, e.g. initial collection uploading.\n\n## Installation\n\n```\npip install qdrant-client\n```\n\n## Examples\n\n\n\nInstance a client\n```python\nfrom qdrant_client import QdrantClient\n\nclient = QdrantClient(host="localhost", port=6333)\n```\n\nCreate a new collection\n```python\nclient.recreate_collection(\n    collection_name="my_collection",\n    vector_size=100\n)\n```\n\nGet info about created collection\n```python\nmy_collection_info = client.http.collections_api.get_collection("my_collection")\nprint(my_collection_info.dict())\n```\n\nSearch for similar vectors\n\n```python\nquery_vector = np.random.rand(100)\nhits = client.search(\n    collection_name="my_collection",\n    query_vector=query_vector,\n    query_filter=None,  # Don\'t use any filters for now, search across all indexed points\n    append_payload=True,  # Also return a stored payload for found points\n    top=5  # Return 5 closest points\n)\n```\n\nSearch for similar vectors with filtering condition\n\n```python\nfrom qdrant_client.http.models import Filter, FieldCondition, Range\n\nhits = client.search(\n    collection_name="my_collection",\n    query_vector=query_vector,\n    query_filter=Filter(\n        must=[  # These conditions are required for search results\n            FieldCondition(\n                key=\'rand_number\',  # Condition based on values of `rand_number` field.\n                range=Range(\n                    gte=0.5  # Select only those results where `rand_number` >= 0.5\n                )\n            )\n        ]\n    ),\n    append_payload=True,  # Also return a stored payload for found points\n    top=5  # Return 5 closest points\n)\n```\n\nCheck out [full example code](tests/test_qdrant_client.py)\n\n### gRPC\n\ngRPC support in Qdrant client is under active development.\nBasic classes could be found [here](qdrant_client/grpc/__init__.py).\n\nTo enable (much faster) collection uploading with gRPC, use the following initialization:\n\n```python\nfrom qdrant_client import QdrantClient\n\nclient = QdrantClient(host="localhost", grpc_port=6334, prefer_grpc=True)\n```\n',
    'author': 'Andrey Vasnetsov',
    'author_email': 'andrey@qdrant.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qdrant/qdrant_client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
