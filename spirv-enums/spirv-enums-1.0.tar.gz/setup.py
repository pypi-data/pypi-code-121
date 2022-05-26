# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spirv_enums']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'spirv-enums',
    'version': '1.0',
    'description': 'A lightweight Python packages containing enums for the SPIR-V language',
    'long_description': '# SPIRV-Enums\nA lightweight Python packages containing enums for the SPIR-V language\n',
    'author': 'Rayan Hatout',
    'author_email': 'rayan.hatout@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rayanht/SPIRV-Enums',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
