# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['robo_slack_bot']

package_data = \
{'': ['*']}

install_requires = \
['Flask-Cors>=3.0.10,<4.0.0',
 'elasticsearch>=8.2.0,<9.0.0',
 'recipe-scrapers>=13.32.1,<14.0.0',
 'slack-cleaner2>=3.1.1,<4.0.0',
 'slack>=0.0.2,<0.0.3',
 'slackclient>=2.9.4,<3.0.0',
 'slackeventsapi>=3.0.1,<4.0.0',
 'validators>=0.19.0,<0.20.0']

entry_points = \
{'console_scripts': ['eve-bot = robo_slack_bot.eve_bot:main',
                     'recipe-scraper = robo_slack_bot.recipe_scraper:main',
                     'slack-channel-cleaner = '
                     'robo_slack_bot.slack_cleaner:main']}

setup_kwargs = {
    'name': 'robo-slack-bot',
    'version': '0.2.1.dev0',
    'description': 'It is a slackbot',
    'long_description': None,
    'author': 'John Stilia',
    'author_email': 'stilia.johny@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
