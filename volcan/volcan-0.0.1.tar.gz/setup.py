# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['volcan',
 'volcan.backend',
 'volcan.frontend',
 'volcan.frontend.lexer',
 'volcan.frontend.parser']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'volcan',
    'version': '0.0.1',
    'description': 'A modern, strongly-typed, general-purpose programming language.',
    'long_description': '# Volcan\n\nA modern, strongly-typed, general-purpose programming language.\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
