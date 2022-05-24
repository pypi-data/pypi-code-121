# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whatsapp_business_api']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.78.0,<0.79.0', 'pydantic>=1.9.1,<2.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'whatsapp-business-api',
    'version': '0.1.4',
    'description': 'A wrapper for WhatsApp Business Cloud API provided by Meta.',
    'long_description': "# Whatsapp Business Cloud API\n\nThis repository is a wrapper for Meta's Whatsapp Business Cloud API.\n\n## Use\n\n```python\nfrom whatsapp_business_api import WhatsappAPI\n\nphone_number_id = 'YOUR_SENDER_ID'\naccess_token = 'YOUR_ACCESS_TOKEN'\n\nw = WhatsappAPI(phone_number_id=phone_number_id,\n                access_token=access_token)\n\nw.send_text_message(to='49xxxxxxxxxxx', message='This is a test!')\n```\n",
    'author': 'Abdurrahman Dilmac',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cerob/whatsapp-business-api-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
