# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aworda', 'aworda.lbot']

package_data = \
{'': ['*']}

install_requires = \
['beanie>=1.11.0,<2.0.0', 'graia-ariadne>=0.6.16,<0.7.0']

setup_kwargs = {
    'name': 'aworda-lbot',
    'version': '0.0.1',
    'description': 'make ariadne better',
    'long_description': None,
    'author': 'Little-LinNian',
    'author_email': '2544704967@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
