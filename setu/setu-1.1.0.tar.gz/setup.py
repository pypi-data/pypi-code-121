# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['setu', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.4.0,<3.0.0',
 'marshmallow-oneofschema>=3.0.1,<4.0.0',
 'marshmallow>=3.14.1,<4.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'setu',
    'version': '1.1.0',
    'description': "Python package to connect to Setu's UPI Deep Link APIs.",
    'long_description': '# Setu UPI DeepLinks: Python SDK\n\n`setu` is a Python SDK for accessing Setu’s [UPI Deeplinks](https://docs.setu.co/collect/biller/upi-deep-links) APIs. The SDK is designed with ease of access in mind, with native Python class objects for inputs & ouputs and custom exceptions.\n\n[![Version](https://img.shields.io/pypi/v/setu?color=%2320014B)](https://pypi.org/project/setu-python-sdk)\n[![Downloads](https://img.shields.io/pypi/dw/setu?color=%23FEB452)](https://www.npmjs.org/package/@setu/upi-deep-links)\n[![License](https://img.shields.io/pypi/l/setu?color=%23FE90A0)](LICENSE.md)\n\n<img src="assets/deeplinks.png" alt="SDK in action" width="100%">\n\nPython package to connect to Setu\'s UPI Deep Link APIs\n\n## Getting started\n\n[SDK documentation →](https://opensource.setu.co/setu-python-sdk)\n[Full documentation →](https://docs.setu.co/payments/upi-deeplinks)\n[Product overview →](https://setu.co/payments/upi-deeplinks)\n\n### Installation\n\n```bash\npip install setu\n```\n\n### Features\n\n-   Full support for latest UPI Deeplinks APIs\n-   Native Python class objects for all inputs & responses\n-   Allows both [JWT](https://docs.setu.co/payments/upi-deeplinks/resources/jwt) & [OAuth](https://docs.setu.co/payments/upi-deeplinks/resources/oauth) authentication mechanisms\n-   `SANDBOX` mode to test integration & `PRODUCTION` for live data\n-   Internal mechanism for OAuth authentication to automatically re-fetch token when current one expires, and retry all failed requests.\n\n## Examples\n\n### Setup\n\n```python\nfrom setu import Deeplink\nfrom setu.contract import RefundRequestItem, SetuAPIException\n\ndl = Deeplink(\n    scheme_id="c4f57443-dc1e-428f-8c4e-e5fd531057d2",\n    secret="5b288618-473f-4193-ae1b-8c42f223798e",\n    product_instance_id="861023031961584801",\n    auth_type="OAUTH",\n    mode="SANDBOX",\n)\n```\n\n### Generate UPI payment link\n\n```python\nbill_amount = 100\ntry:\n    link = dl.create_payment_link(\n        amount_value=bill_amount,\n        biller_bill_id="test_transaction_1234",\n        amount_exactness="EXACT",\n        payee_name="Python SDK unittest",\n        transaction_note="unittest transaction",\n    )\n    assert link.payment_link.upi_id == "refundtest@kaypay"\nexcept SetuException as e:\n    assert False\n```\n\n### Get Payment Link Status\n\n```python\ntry:\n    link_status = dl.check_payment_status(link.platform_bill_id)\n    assert link_status.status == "BILL_CREATED"\nexcept SetuAPIException as e:\n    assert False\n```\n\n# Trigger mock payment for UPI payment link (Sandbox only)\n\n```python\ntry:\n    credit_response = dl.trigger_mock_payment(\n        float(bill_amount) / 100, link.payment_link.upi_id, link.platform_bill_id\n    )\nexcept SetuAPIException as e:\n    assert False\n```\n\n### Mock Settlement\n\n```python\ntry:\n    dl.trigger_mock_settlement([credit_response.utr])\nexcept SetuAPIException as e:\n    assert False\n```\n\n### Initiate Refund\n\n```python\ntry:\n    batch_initiate_refund_response = dl.initiate_batch_refund(\n        refunds=[\n            RefundRequestItem(\n                identifier=link.platform_bill_id,\n                identifierType="BILL_ID",\n                refundType="FULL",\n            ),\n        ],\n    )\n    assert batch_initiate_refund_response.refunds[0].status == "MarkedForRefund"\nexcept SetuAPIException as e:\n    assert False\n```\n\n### Get refund batch status\n\n```python\ntry:\n    refund_batch_status_response = dl.get_batch_refund_status(batch_initiate_refund_response.batch_id)\n    assert refund_batch_status_response.refunds[0].bill_id == link.platform_bill_id\nexcept SetuAPIException as e:\n    assert False\n```\n\n### Get individual refund status\n\n```python\ntry:\n    refund_status_response = dl.get_refund_status(batch_initiate_refund_response.refunds[0].id)\n    assert refund_status_response.bill_id == link.platform_bill_id\nexcept SetuAPIException as e:\n    assert False\n```\n\n## Contributing\n\nHave a look through existing [Issues](https://github.com/SetuHQ/setu-python-sdk/issues) and [Pull Requests](https://github.com/SetuHQ/setu-python-sdk/pulls) that you could help with. If you\'d like to request a feature or report a bug, please [create a GitHub Issue](https://github.com/SetuHQ/setu-python-sdk/issues) using the template provided.\n\n[See contribution guide →](CONTRIBUTING.md)\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n\n## License\n\nMIT. Have at it.\n',
    'author': 'Naresh R',
    'author_email': 'ghostwriternr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SetuHQ/setu-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
