# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['watchmen_rest', 'watchmen_rest.system', 'watchmen_rest.util']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.75.1,<0.76.0',
 'jsonschema>=4.4.0,<5.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'python-jose>=3.3.0,<4.0.0',
 'uvicorn>=0.17.6,<0.18.0',
 'watchmen-auth==16.1.4',
 'watchmen-storage==16.1.4']

setup_kwargs = {
    'name': 'watchmen-rest',
    'version': '16.1.4',
    'description': '',
    'long_description': None,
    'author': 'botlikes',
    'author_email': '75356972+botlikes456@users.noreply.github.com',
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
