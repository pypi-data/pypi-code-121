# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qapi_sdk', 'qapi_sdk.logs']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=0.20.0,<0.21.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'qapi-sdk',
    'version': '0.1.3',
    'description': 'QAPI SDK provides a library of classes for working with Query API in your Python code.',
    'long_description': '# QAPI SDK\n\nQAPI SDK provides a library of classes for working with Query API in your Python code.\n\n## Requirements\n\n    * Python 3.6+\n\n## Installation\n\n```bash\npip install qapi-sdk \n```\n\n## Environment Variables\n\n- `QAPI_URL`: QAPI API URL\n- `EMAIL`: Your email\n\n## Examples\n\n### Query\n\n- `FEED ID`: The table must exist in Athena.\n- `QUERY ID`: The query id is used as an identifier for the query. Query id must be unique. Once you have retrieved your\n  data from S3 it is advised to delete the query.\n- `SQL`: The SQL query to be executed.\n\n```python\nimport time\n\nfrom dotenv import load_dotenv\n\nfrom qapi_sdk import Query\n\nload_dotenv()\n\n# Step 1: Assign your FEED ID, QUERY ID, and SQL QUERY\nfeed_id = "[FEED/TABLE NAME]"\nquery_id = "[QUERY NAME]"\nquery = f"SELECT * FROM {feed_id}"\n\n# Step 2: Create a Query object\nmy_query = Query(\n    feed_id=feed_id,\n    query_id=query_id\n)\n\n# Step 3: Execute the query push\nmy_query.push_query(sql=query)\n\n# Step 4: Wait for the query to complete\nwhile my_query.query_status():\n    print("Waiting for query to complete...")\n    time.sleep(10)\n\n# Step 5 (Optional): Delete the query\nmy_query.delete_query()\n```\n\n\n\n',
    'author': 'TheBridgeDan',
    'author_email': '97176881+TheBridgeDan@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
