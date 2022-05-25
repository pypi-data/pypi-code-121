# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['los_docusign', 'los_docusign.migrations', 'los_docusign.utils']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.1.13,<4.0.0',
 'PyJWT==2.4',
 'django-environ>=0.4.5,<0.5.0',
 'django-lc-utils>=0.2.1,<0.3.0',
 'django-model-utils>=4.1.1,<5.0.0',
 'django-utils-six>=2.0,<3.0',
 'docusign-esign>=3.6.0,<4.0.0',
 'phonenumbers==8.12.26',
 'psycopg2-binary>=2.9.2,<3.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'los-docusign',
    'version': '0.5.9',
    'description': 'Docusign Django Wrapper for integrating DocuSign with Django Application',
    'long_description': '# Django-DocuSign\nDjango wrapper app for DocuSign functionalities\n\n`pip install django-docusign`\n\n## Running Tests\nWe have a unit test defined for testing the los application.\nThis can be executed using the below command.\n\n```\npython manage.py test\n```\n\n## Usage\nIn order to use the system you must add los_docusign.apps.LosDocusignConfig to your installed apps in your settings.py file.\n```python\nINSTALLED_APPS = [\n    \'los_docusign\'\n]\n```\n\nTest file has the sample implementation of the test_app\n\n## Functions in client.py\n1.  generate_docusign_preview_url(dict)\n\n    Params required in dict:\n    -   "envelope_id"\n    -   "authentication_method"\n    -   "email"\n    -   "user_name"\n    -   "client_user_id"\n    -   "return_url"\n\n2. create_envelope(payload)\n\n    Params required:\n    -   DocuSign payload in JSON format\n\n3. download_docusign_document(dict)\n\n    Params required in dict:\n    -   "envelope_id"\n    -   "doc_download_option"\n        -   Valid Values:\n            1. archive - If the document to be downloaded in zip format.\n            2. combined - If the document to be downloaded as a combined document.\n\n4. process_docusign_webhook(xml_string)\n\n    Params required:\n    -   Webhook XML string received from Docusign.\n\n    Response dict:\n        {\n            "envelopeId": "c57ec066-c5fa-4aa0-873d-6f285d70242a",\n            "envelope_status": "sent",\n            "recipients": [\n                {\n                    "recipient_id": "a7f73f21-c4ff-4bcb-97c4-b03c91b8528a",\n                    "email": "test@test.com",\n                    "name": "John Nash",\n                    "status": "autoresponded"\n                },\n                {\n                    "recipient_id": "511b2ad3-6650-4773-a6b4-47f64a0ccdaf",\n                    "email": "jerry@test.com",\n                    "name": "Jerry Tunes",\n                    "status": "created"\n                },\n                {\n                    "recipient_id": "0851505f-5af2-42df-bce4-9e0ebe8bd2e2",\n                    "email": "tom@test.com",\n                    "name": "Tom Tunes",\n                    "status": "created"\n                }\n            ]\n        }\n\n5. update_envelope_and_resend(envelope_id, signers_data)\nThis function is used to update the email/phone number of the signer.\nThis is also used to resend the same envelope to the signers. For resending, recipientId and email are mandatory.\n\n    Params required:\n    -   envelope_id - The envelope id for which we need to update the signers information or send the same envelope to the signers.\n    -   signers_data - The signer array which has the information about the signers that needs to be updated.\n    Params required in signers_data:\n    -   email - The email of the signer.\n    -   recipientId - The recipient id of the signer\n    -   phone  - The phone number of the signer (optional)\n\n    signers_data example:\n    [\n        {\n            "recipientId":"123456",\n            "email":"test@test.com",\n            "phone":"1234567890"\n        }\n    ]\n\n5. update_envelope_status(status_info):\nThis function is used to update the status of the envelope.\n\n    Params required:\n    -   status_info - The dictionary variale which has the following parameters.\n        - envelope_id - The envelope id for which the status needs to be updated\n        - status - The status in which we need to set the envelope\n        - reason - The reason (if applicable) to be set for the status change. This will be visible to the signer\n\n    status_info example:\n    {\n        "envelope_id":"b1435c5d-3d67-46e8-ab6a-54789f42924e",\n        "status":"voided",\n        "reason":"Voiding an envelope"\n    }\n    \n',
    'author': 'tejasb',
    'author_email': 'tejas@thesummitgrp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Lenders-Cooperative/Django-DocuSign',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
