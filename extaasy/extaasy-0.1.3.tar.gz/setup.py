# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['connect_lib', 'connect_lib.client', 'connect_lib.flows']

package_data = \
{'': ['*']}

install_requires = \
['Faker',
 'connect-extension-runner>=25.0.0,<26.0.0',
 'mock>=4.0.3,<5.0.0',
 'responses>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'extaasy',
    'version': '0.1.3',
    'description': 'CloudBlue Connect EaaS Extension Library',
    'long_description': '# Welcome to Connect Extension Library !\n\n\nCloudBlue Connect EaaS Extension Library\n\n\n\n## License\n\n**Connect Extension Lib** is licensed under the *Apache Software License 2.0* license.\n\n',
    'author': 'Ingram Micro',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
