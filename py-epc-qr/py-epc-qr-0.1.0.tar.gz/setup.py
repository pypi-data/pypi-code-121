# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_epc_qr']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.0,<10.0.0',
 'PyYAML>=6.0,<7.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'qrcode>=7.3.1,<8.0.0']

setup_kwargs = {
    'name': 'py-epc-qr',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'timueh',
    'author_email': 'tillmann.muehlpfordt@kit.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
