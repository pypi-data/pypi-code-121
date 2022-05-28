# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gelatin_extract',
 'gelatin_extract.base',
 'gelatin_extract.io',
 'gelatin_extract.json',
 'gelatin_extract.json.schema',
 'gelatin_extract.xml',
 'gelatin_extract.xml.io',
 'gelatin_extract.xml.schema']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.8.0,<5.0.0', 'python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'gelatin-extract',
    'version': '0.1.0',
    'description': 'XML and JSON deserialization',
    'long_description': None,
    'author': 'Parker Hancock',
    'author_email': '633163+parkerhancock@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
