# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uc_browser']

package_data = \
{'': ['*']}

install_requires = \
['selenium-wire>=4.6.4,<5.0.0',
 'stem>=1.8.0,<2.0.0',
 'undetected-chromedriver>=3.1.5,<4.0.0',
 'webdriver-manager>=3.5.4,<4.0.0']

setup_kwargs = {
    'name': 'uc-browser',
    'version': '0.2.0',
    'description': '',
    'long_description': '# browser\nModulo que implementa metodos para uso com selenium.\n',
    'author': 'Thiago Oliveira',
    'author_email': 'thiceconelo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ceconelo/browser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
