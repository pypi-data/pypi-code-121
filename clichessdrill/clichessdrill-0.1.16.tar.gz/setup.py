# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clichessdrill']

package_data = \
{'': ['*']}

install_requires = \
['chess>=1.9.0,<2.0.0', 'docopt>=0.6.2,<0.7.0', 'python-chess>=1.999,<2.0']

entry_points = \
{'console_scripts': ['clichessdrill = clichessdrill.main:main']}

setup_kwargs = {
    'name': 'clichessdrill',
    'version': '0.1.16',
    'description': '',
    'long_description': '# clichessdrill\npractice chess drills in a command line interface\n\n### Installation\nvia PyPI:\n\n```pip install clichessdrill```\n\nfrom source:\n\n```poetry install```\n\n### Play\nTo run and play one round:\n\n```chessdrill```\n\nTo play any number of drills in a row, use the `-n` option. For example:\n```\nchessdrill -n 10\n```\nIf no training file is specified during the call, a standard built in drill plan \nwill be used.\n\n##### Custom drill training plans\nIn addition, the user has the option to use their own custom training plan. To play \nand execute a custom drill plan saved as a json file use the `-f` option to \npoint to the path of the training file:\n\n```\nchessdrill -n 20 -f my/training/file.json\n```\nThe layout of the drill plan is a representation of the decision tree. As an example:\n```json\n{\n  "name": "my drill plan",\n  "play": {\n    "white": {\n      "c4": {\n        "e5": {\n          "e4": {\n            "Nf6": {\n              "Nc3": {}\n            },\n            "c5": {\n              "d3": {}\n            }\n          }\n        },\n        "e6": {\n          "Nc3": {}\n          }\n        },\n        "Nf6": {\n          "Nc3": {}\n          }\n        },\n        "b6": {\n          "d4": {}\n        }\n      }\n    },\n    "black": {\n      "e4": {\n        "c6": {}\n      },\n      "d4": {\n        "d5": {\n          "Bf4": {\n            "e6": {\n              "Nf3": {\n                "Nf6": {}\n              }\n            }\n          }\n        }\n      }\n    }\n  }\n}\n```\nThe subsections for the respective game color represent the decision branches according to which the user should \nrespond while playing either of the sides. The decision trees can be arbitrarily deep and leaves should terminate \nwith empty brackets `{}`\n### Example Game Play\n![game play 1](https://raw.githubusercontent.com/danielschweigert/clichessdrill/main/docs/screenshots/game_play_1.png)\n![game play 2](https://raw.githubusercontent.com/danielschweigert/clichessdrill/main/docs/screenshots/game_play_2.png)\n![game play 3](https://raw.githubusercontent.com/danielschweigert/clichessdrill/main/docs/screenshots/game_play_3.png)',
    'author': 'Daniel Schweigert',
    'author_email': 'dan.schweigert@gmail.com',
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
