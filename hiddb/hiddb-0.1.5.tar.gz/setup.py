# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hiddb']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.3.0,<3.0.0', 'aiohttp>=3.8.1,<4.0.0', 'asyncio>=3.4.3,<4.0.0']

setup_kwargs = {
    'name': 'hiddb',
    'version': '0.1.5',
    'description': 'Python SDK for HIDDB',
    'long_description': '# HIDDB Python SDK\n\nThe official SDK for the [HIDDB](https://hiddb.com) vector database.\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install the SDK.\n\n```bash\npip install hiddb\n```\n\n## Usage\n\nCreate a collection within a database `<your database_id>`.\n\n```python\nfrom hiddb.synchronous import HIDDB\n\nhiddb = HIDDB("<key>", "<secret>")\n\n# Create a collection named \'wordvectors\'\nhiddb.create_collection(database_id="<your database_id>", collection_id="wordvectors")\n```\n\nCreate an index within this collection:\n\n```python\n# Create an index on field \'vector\' within the collection and dimension 300\nhiddb.create_index(\n    database_id="<your database_id>",\n    collection_name=\'wordvectors\',\n    field_name="vector",\n    dimension=300\n)\n```\n\nInsert documents like that:\n\n```python\ndocument = {\n    "vector": [0.0]*300,\n    "id": "my first document"\n}\n\nhiddb.insert_document(\n    database_id=database_id,\n    collection_name=\'wordvectors\',\n    documents=[document]\n)\n```\n\nSearch for nearest documents:\n\n```python\nsimilar_words = hiddb.search_nearest_documents(\n    database_id="<your database_id>",\n    collection_name=\'wordvectors\',\n    field_name="vector",\n    vectors=[[42.0]*300],\n    max_neighbors=10\n)\n```\n\nMore examples and a more detailed documentation will follow soon 🚀\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n',
    'author': 'Benjamin Bolbrinker',
    'author_email': 'benjamin.bolbrinker@hiddb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://hiddb.com',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
