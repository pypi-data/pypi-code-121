# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vinca', 'vinca._lib']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.4.0,<0.5.0', 'prompt-toolkit>=3.0.29,<4.0.0', 'rich>=12.4.1,<13.0.0']

entry_points = \
{'console_scripts': ['vinca = vinca:run']}

setup_kwargs = {
    'name': 'vinca',
    'version': '2.3.4',
    'description': 'Spaced Repetition CLI',
    'long_description': '## Synopsis\n\n`VINCA` is a command-line spaced-repetition study tool.\n\n## Installing Vinca\n\n`pip install vinca`\n\n## Basic commands\n\n|command           |   description                            |  \n|------------------|------------------------------------------|  \n|--help            |   full screen help                       |  \n|basic             |   create question and answer cards       |  \n|review            |   study your cards                       |  \n|browse            |   interactively manage your cards        |  \n|count             |   simple summary statistics              |  \n|tutorial review   |   study a tutorial deck of twenty cards  |  \n\n## Screenshots\n\n![vinca stats](./utils/stats.png)\n\n### basic commands\n![basic screencast](./utils/screencast.gif?)\n',
    'author': 'Oscar Laird',
    'author_email': 'olaird25@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/oscarlaird/vinca-SRS',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
