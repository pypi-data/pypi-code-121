# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eve_client']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl==1.4.0', 'python-dateutil==2.8.2', 'requests==2.26.0']

setup_kwargs = {
    'name': 'eve-client',
    'version': '1.0.1',
    'description': 'EVE API client from Exodus Intelligence LLC.',
    'long_description': '# Exodus Intelligence API Client\n\n## Prerequisites\n\nAn Exodus Intelligence Account is required. Visit https://vpx.exodusintel.com to obtain an account.\n\n[Python](https://www.python.org/downloads/) 3.8 or newer is required.\n&nbsp;\n## Getting started\n\nInstallation via pip (binary):\n\n```bash\n$ pip install eve_client-1.0.0c1-py3-none-any.whl\n```\n[//]: # (Installation from binary: [TODO])\n[//]: # ()\n[//]: # (Download the wheel file from <here>:)\n[//]: # ()\n[//]: # (```bash)\n[//]: # ($ pip install exodus_eve.whl)\n[//]: # (```)\n[//]: # ()\n[//]: # (Installation from source:)\n[//]: # ()\n[//]: # (```bash)\n[//]: # ($ git clone url)\n[//]: # ($ cd eve)\n[//]: # ($ pip install -r requirements.txt)\n[//]: # (```)\n\n## Usage\n\n```python\n>>> from eve_client import eve\n>>> email = "myemail@provider.com"\n>>> password = "abc123"\n>>> key = "My_Exodus_Intelligence_API_Key"\n>>> eve = eve.EVEClient(email, password, key)\n>>> eve.get_recent_vulns()[\'data\'][\'items\'][0]\n>>> {\'access_vector\': \'...\',\n     \'attack_vector\': ...,\n     \'cpes\': ...,\n     \'created_timestamp\': \'...\',\n     \'cves\': [\'...\'],\n     \'cvss\': ...,\n     \'description\': "...",\n     \'identifier\': \'...\',\n     \'modified_timestamp\': \'...\',\n     \'product\': \'...\',\n     \'publish_date\': \'...\',\n     \'reported\': ...,\n     \'updated_date\': \'...\',\n     \'vendor\': \'GitLab\',\n     \'xi_scores\': ...,\n     \'zdis\': ...}\n>>>\n```\n## eve_client Classes and Functions\n\n### Classes\n[//]: # (    builtins.object)\n[//]: # (        Client)\n\n#### class Client(builtins.object)\n\n`Client(email, password, key=None) -> None`\n\nAn object that communicates with the Exodus API.\n\nThis class includes methods for requesting vulnerabilities and reports from the Exodus Intelligence API as well as methods and functions in support of those.\n\nExample of connection initiation:\n\n    >>> from eve_client import eve\n    >>> exodus_api = eve.EVEClient(\'email\', \'password\', \'private_key\')\n\nNote: See `help(Client)` for more information.\n\n##### Methods\n\n`__init__(self, email, password, key=None) -> None`\n\nInitializes and returns a newly allocated client object.\n\n*Parameters*\n\n    email (str): Email address registered with Exodus Intelligence.\n    password (str): User password\n    key (str, optional): Exodus Intelligence API key. Defaults to None.\n&nbsp;\n\n`decrypt_bronco_in_report(self, report, bronco_public_key)`\n\nDecrypts the content of a report using a private and public key.\n\n*Parameters*\n\n    report (object): The encrypted message.\n    bronco_public_key (str): The public key\n\n*Returns*\n\n    dict: A dictionary object representing the report.\n&nbsp;\n\n`generate_key_pair(self)`\n\nGenerates a key pair.\n\n*Raises*\n\n    InvalidStateError: Could not set the public key.\n    InvalidStateError: Could not confirm the public key.\n\n*Returns*\n\n    tuple: A key pair (sk, pk)\n&nbsp;\n\n`get_access_token(self)`\n\nObtain access token.\n\n*Raises*\n\n    ConnectionError: When a connection to API is unavailable.\n\n*Returns*\n\n    str: The token.\n&nbsp;\n\n`get_bronco_public_key(self)`\n\nGet server public key.\n\n*Returns*\n\n    str: A string representation of a public key.\n&nbsp;\n\n`get_recent_reports(self, reset=1)`\n\nGet list of recent reports.\n\n*Parameters*\n\n    reset (int): Number of days in the past to reset.\n\n*Returns*\n\n    dict: Returns a list of reports.\n&nbsp;\n\n`get_recent_vulns(self, reset=None)`\n\nGet all vulnerabilities within 60 days of the user\'s stream marker; limit of 50 vulnerabilities can be returned.\n\n*Parameters*\n\n    reset (int): Reset the stream maker to a number of days in the past.\n\n*Returns*\n\n    dict: Returns a list of vulnerabilities.\n&nbsp;\n\n`get_report(self, identifier)`\n\nGet a report by identifier.\n\n*Parameters*\n\n    identifier (str): String representation of report id.\n\n*Returns*\n\n    dict: Returns either a report in json format\n&nbsp;\n\n`get_vuln(self, identifier)`\n\nRetrieve a ulnerability by Exodus Intelligence identifier or by CVE.\n\n*Parameters*\n\n    identifier (str): String representation of vulnerability id.\n\n*Returns*\n\n    dict: Returns either a report in json format\n&nbsp;\n\n`get_vulns_by_day(self)`\n\nGet vulnerabilities by day.\n\n*Returns*\n\n    dict: Returns vulnerabilities list.\n&nbsp;\n\n`handle_reset_option(self, reset)`\n\nReset number of days.\n\n*Parameters*\n\n    reset (int): Number of days in the past to reset\n\n*Returns*\n\n    datetime:  A date\n\n##### Data descriptors\n\n`__dict__`\n\nDictionary for instance variables (if defined).\n\n`__weakref__`\n\nList of weak references to the object (if defined).\n\n##### Data and other attributes\n\n`url = \'https://vpx.exodusintel.com/\'`\n\n### Functions\n\n`verify_email(email)`\n\nVerify email\'s format.\n\n*Parameters*\n\n    email: email address.\n\n*Raises*\n\n    ValueError: If `email` is not a string.\n    ValueError: If `email` format is invalid.\n\n*Returns*\n\n    bool: True\n',
    'author': 'Exodus Intelligence LLC',
    'author_email': 'eng@exodusintel.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/ExodusIntelligence/eve_client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
