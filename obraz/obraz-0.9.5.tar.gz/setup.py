# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['obraz']

package_data = \
{'': ['*'],
 'obraz': ['scaffold/*',
           'scaffold/_layouts/*',
           'scaffold/_posts/*',
           'scaffold/css/*']}

install_requires = \
['Jinja2>=3.1.1,<4.0.0',
 'Markdown>=3.3.6,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'docopt>=0.6.2,<0.7.0']

entry_points = \
{'console_scripts': ['obraz = obraz:main']}

setup_kwargs = {
    'name': 'obraz',
    'version': '0.9.5',
    'description': 'Static blog-aware site generator in Python mostly compatible with Jekyll',
    'long_description': 'Obraz\n=====\n\n**Obraz** (*Russian: Образ*). IPA: /ˈobrəs/ *n.*\n\n1. Image, the result of applying a function to an argument\n2. A static blog-aware site generator in Python mostly compatible with Jekyll\n\n\nWhy?\n----\n\nThere are many static site generators. Why choose Obraz?\n\n* Written in [Python][1]\n* Single source file less than [800][2] lines of code\n* Mostly [compatible][3] with the popular Jekyll\n\n\nDocumentation\n-------------\n\nVisit the [Obraz homepage][4] for more info.\n\n\n[1]: https://xkcd.com/353/\n[2]: https://github.com/vlasovskikh/obraz/blob/master/obraz/__init__.py\n[3]: https://obraz.pirx.ru/jekyll.html\n[4]: https://obraz.pirx.ru/\n',
    'author': 'Andrey Vlasovskikh',
    'author_email': 'andrey.vlasovskikh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://obraz.pirx.ru/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
