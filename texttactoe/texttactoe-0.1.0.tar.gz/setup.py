# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['texttactoe']

package_data = \
{'': ['*']}

install_requires = \
['textual>=0.1.18,<0.2.0']

entry_points = \
{'console_scripts': ['texttactoe = texttactoe.__main__:run']}

setup_kwargs = {
    'name': 'texttactoe',
    'version': '0.1.0',
    'description': 'A TUI to play tictactoe.',
    'long_description': '# TextTacToe\nThis is an TUI App for playing TicTacToe built using [Textual](https://github.com/willmcgugan/textual/) in Python3.\n\n![View Of TextTacToe](img/TextTacToe.gif)\n\n>**NOTE:** Due to the fact that textual t is still in the develepment stage, I reccomend you install this only in virtual env. This app will probably change heavily as textual changes.\n\n## Dependencies\n\nTextual:\n```\npython -m pip install textual \n```\n\n## Install\n\n```\npython -m pip install texttactoe\n```\n## Run\n\nIf installed correctly, you should be able to run 1 of 2 ways, as a python module or a standalone script:\n\n```\npython -m texttactoe\n```\nor\n```\ntexttactoe\n```\n The following options are available for customization. Note that the color options currently do not check whether they are a valid colors. We use textual/rich to customize the color and so it mus be a valid choice from these frameworks.\n```\nusage: texttactoe [-h] [-v] [-p1 PLAYER1] [-p2 PLAYER2] [-c1 COLOR1] [-c2 COLOR2] [-r]\n\nA tictactoe TUI.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -v, --version         display version information\n  -p1 PLAYER1, --player1 PLAYER1\n                        Name of Player1\n  -p2 PLAYER2, --player2 PLAYER2\n                        Name of Player2\n  -c1 COLOR1, --color1 COLOR1\n                        Color of Player1\n  -c2 COLOR2, --color2 COLOR2\n                        Color of Player2\n  -r, --random          Randomize player colors\n```',
    'author': 'Jose Medina',
    'author_email': 'jose.amedina96@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JoseAndresMedina/TextTacToe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
