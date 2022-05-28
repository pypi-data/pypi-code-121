# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_epc_qr']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.0,<10.0.0',
 'PyYAML>=6.0,<7.0',
 'qrcode>=7.3.1,<8.0.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['epcqr = py_epc_qr.cli:main']}

setup_kwargs = {
    'name': 'py-epc-qr',
    'version': '0.1.2.1',
    'description': 'Generate EPC-compatible QR codes for wire transfers',
    'long_description': '# Create QR codes for wire transfers\n\nSick of copy-and-pasting IBANs to forms?\nWhy not just scan a QR code and have your favorite banking app take care of the rest?\n\nWhy not be generous and support wikipedia with 123,45€?\nGrab your phone and scan the image.\n\n![Support Wikipedia with 123,45 €](tests/data/qr_version_002.png "Support Wikipedia with 123,45 €")\n\n[The create QR code complies with the European Payments Council (EPC) Quick Response (QR) code guidelines.](https://en.wikipedia.org/wiki/EPC_QR_code)\n\nDisclaimer: The author of this code has no affiliation with the EPC whatsoever.\nHenceforth, you are welcome to use the code at your own dispense, but any use is at your own (commercial) risk.\n\n## Installation\n\nYou can easily install the Python package via pip.\n\n```python\npip install py-epc-qr\n```\n\n## Usage\n\nYou can use the package as part of your own code or as a standalone command line interface (CLI).\n\n### Code\n\n```python\nfrom py_epc_qr.transaction import consumer_epc_qr\nepc_qr = consumer_epc_qr(\n    beneficiary= "Wikimedia Foerdergesellschaft",\n    iban= "DE33100205000001194700",\n    amount= 123.45,\n    remittance= "Spende fuer Wikipedia"\n    )\nepc_qr.to_qr()\n```\n\n### CLI\n\n<todo>\n\n### From interaction\n\n<todo>\n\n#### From template\n\n<todo>\n\n## Limitations\n\nCurrently, the EPC specifications are implemented only to work with IBAN-based consumer wire transfers within the European Economic Area.',
    'author': 'timueh',
    'author_email': 't.muehlpfordt@mailbox.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/timueh/py-epc-qr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
