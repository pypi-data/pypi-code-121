# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bambooapi_client',
 'bambooapi_client.client',
 'bambooapi_client.openapi',
 'bambooapi_client.openapi.api',
 'bambooapi_client.openapi.apis',
 'bambooapi_client.openapi.model',
 'bambooapi_client.openapi.models',
 'bambooapi_client.testing',
 'bambooapi_client.testing.factory']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21,<1.22',
 'pandas>=1.3,<1.4',
 'python_dateutil>=2.8,<2.9',
 'urllib3>=1.26,<1.27']

setup_kwargs = {
    'name': 'bambooapi-client',
    'version': '1.12.1',
    'description': 'Bamboo Flexibility API',
    'long_description': "# Python client for Bamboo REST API\n\n[![PyPI Version](https://img.shields.io/pypi/v/bambooapi-client.svg)](https://pypi.org/project/bambooapi-client/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/bambooapi-client.svg)](https://pypi.org/project/bambooapi-client/)\n\n\nThe Bamboo REST API provides access to flexibility assets managed by Bamboo \nEnergy:\n\n- Create and list flexibility sites & assets\n- Post and get measurements for specific assets\n- Obtain activations for specific assets\n\nThe sandboxed version of the API to be used for development & testing is \navailable at: https://dev-sandbox.bambooenergy.tech/v1/docs\n\n## Installation & Usage\n\nYou can install the package directly using:\n\n```sh\npip install bambooapi-client\n```\n\nThen import the package:\n\n```python\nimport bambooapi_client\n```\n\n## Getting Started\n\nFirst, import the `BambooAPIClient` class and initialize it with the API URL \nand the API bearer token that was assigned to you.\n\n```python\nfrom bambooapi_client import BambooAPIClient\n\nbambooapi_url = 'https://dev-sandbox.bambooenergy.tech/v1'\nbambooapi_token = 'your_token'\n\nclient = BambooAPIClient(url=bambooapi_url, token=bambooapi_token)\n```\n\nYou can now access the **Sites API** and its methods\n\n```python\nsites_api = client.sites_api()\n```\n\n### Retrieving Site Metadata\n\nYou can then list all the sites related to your API user with the \n`list_sites` command.\n\n```python\nsites_api.list_sites()\n```\n\nGiven a site name, you can obtain a site ID and retrieve the site's detailed \ndescription\n\n```python\nsite_id = sites_api.get_site_id('dummy_building_1')\nsites_api.get_site(site_id)\n```\n\nGiven a site ID, you can now retrieve information about a particular zone or \ndevice\n\n```python\nsites_api.get_thermal_zone(site_id, 'zone1')\nsites_api.get_device(site_id, 'hvac1')\n```\n\n### Retrieving and pushing Site Measurements\n\nGiven a site ID you can retrieve measurements for a specific period.\n\n```python\nfrom datetime import datetime, timezone\nsites_api.read_device_measurements(\n    site_id=site_id,\n    device_name='meter',\n    start=datetime(2021, 6, 3, 8, tzinfo=timezone.utc),\n    stop=datetime(2021, 6, 3, 20, tzinfo=timezone.utc),\n)\n```\n\nOn the other hand, you can also upload new measurements (or update existing \nmeasurements). For that, new measurements must first be converted to a `pandas`\nDataFrame. **1 or more data points can be uploaded at once**.\n\n```python\nimport pandas as pd\n\ndata_points = [\n    {\n        'time': '2021-06-03T07:00:00+00:00',\n        'power': 12.0,\n        'quality': 1\n    },\n    {\n        'time': '2021-06-03T07:15:00+00:00',\n        'power': 15.0,\n        'quality': 1\n    }\n]\n\nnew_data_points = pd.DataFrame.from_records(data_points, index='time')\nsites_api.update_device_measurements(site_id, 'meter', new_data_points)\n```\n\n### Retrieving Activations (BETA)\n\nYou can test how activations would be retrieved with the following command.\n\n```python\nsites_api.read_device_activations(site_id, 'hvac1')\n```\n\nThis feature is not fully operational yet, and the endpoint currently returns mock data only. However, the response format should remain the same.\n",
    'author': 'BambooEnergy',
    'author_email': 'development@bambooenergy.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bambooenergy/mvp-api-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
