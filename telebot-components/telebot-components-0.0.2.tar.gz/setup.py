# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['telebot_components']

package_data = \
{'': ['*']}

install_requires = \
['redis>=4.3.1,<5.0.0', 'telebot-against-war==0.2.1']

setup_kwargs = {
    'name': 'telebot-components',
    'version': '0.0.2',
    'description': 'Framework/toolkit for building Telegram bots with telebot and redis',
    'long_description': '# telebot-components\n\nFramework / toolkit for building bots with [telebot](https://github.com/bots-against-war/telebot).\n\n<!-- ## Development -->\n',
    'author': 'Igor Vaiman',
    'author_email': 'gosha.vaiman@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/bots-against-war/telebot-components',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
