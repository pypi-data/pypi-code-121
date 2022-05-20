# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kicksaw_integration_app_client']

package_data = \
{'': ['*']}

install_requires = \
['kicksaw-integration-utils>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'kicksaw-integration-app-client',
    'version': '1.0.7',
    'description': 'A customized simple-salesforce client for use with the integration app',
    'long_description': "# Overview\n\nTo use Kicksaw's integration app, install [this package](https://login.salesforce.com/packaging/installPackage.apexp?p0=04t8b0000012nE9AAI) in your Salesforce organization.\n\nOnce your org is ready to-go, instantiate the `KicksawSalesforce` class and operate like normal, but note:\n\n- You need to pass the AWS Step Function payload to the class when instantiating\n- Instantiating the client creates an execution object in Salesforce, unless you pass it the id of an already existing execution object\n- All of your bulk operations will have their errors parsed and error objects created in Salesforce if applicable\n\n```python\nfrom kicksaw_integration_app_client import KicksawSalesforce\n\nstep_function_payload = {}\nsalesforce = KicksawSalesforce(connection_object, integration_name, step_function_payload)\n\nsalesforce.bulk.Account.upsert()\n```\n\nFor code examples, please refer to `tests/test_integrations.py`.\n",
    'author': 'Alex Drozd',
    'author_email': 'alex@kicksaw.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kicksaw-Consulting/kicksaw-integration-app-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
