# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlyte']

package_data = \
{'': ['*']}

install_requires = \
['pendulum>=2.1.2,<3.0.0', 'pysqlite3>=0.4.6,<0.5.0']

setup_kwargs = {
    'name': 'sqlyte',
    'version': '0.0.19',
    'description': 'Simple SQLite interface',
    'long_description': '# sqlyte\nSimple SQLite interface\n',
    'author': 'Angelo Gladding',
    'author_email': 'angelo@ragt.ag',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
