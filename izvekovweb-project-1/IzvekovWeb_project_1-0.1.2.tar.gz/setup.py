# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brain_games', 'brain_games.games', 'brain_games.scripts']

package_data = \
{'': ['*']}

install_requires = \
['prompt>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['brain-calc = brain_games.scripts.brain_calc:main',
                     'brain-even = brain_games.scripts.brain_even:main',
                     'brain-games = brain_games.scripts.brain_games:main',
                     'brain-gcd = brain_games.scripts.brain_gcd:main']}

setup_kwargs = {
    'name': 'izvekovweb-project-1',
    'version': '0.1.2',
    'description': 'Игры разума',
    'long_description': None,
    'author': 'Alexander Izvekov',
    'author_email': 'izvekov.web@yandex.ru',
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
