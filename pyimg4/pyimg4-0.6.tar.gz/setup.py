# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyimg4']

package_data = \
{'': ['*']}

install_requires = \
['asn1>=2.5.0,<3.0.0',
 'click>=8.0.0,<9.0.0',
 'pycryptodome>=3.14.1,<4.0.0',
 'pyliblzfse>=0.4.1,<0.5.0',
 'pylzss>=0.3.1,<0.4.0']

entry_points = \
{'console_scripts': ['pyimg4 = pyimg4.__main__:cli']}

setup_kwargs = {
    'name': 'pyimg4',
    'version': '0.6',
    'description': "A Python library/CLI tool for parsing Apple's Image4 format.",
    'long_description': '<p align="center">\n<img src=".github/assets/icon.png" alt="https://github.com/m1stadev/PyIMG4" width=256px> \n</p>\n\n<h1 align="center">\nPyIMG4\n</h1>\n<p align="center">\n  <a href="https://github.com/m1stadev/PyIMG4/blob/master/LICENSE">\n    <image src="https://img.shields.io/github/license/m1stadev/PyIMG4">\n  </a>\n  <a href="https://github.com/m1stadev/PyIMG4/stargazers">\n    <image src="https://img.shields.io/github/stars/m1stadev/PyIMG4">\n  </a>\n  <a href="https://github.com/m1stadev/PyIMG4">\n    <image src="https://img.shields.io/tokei/lines/github/m1stadev/PyIMG4">\n  </a>\n  <a href="https://github.com/m1stadev/PyIMG4">\n    <image src="https://img.shields.io/github/workflow/status/m1stadev/PyIMG4/Run%20tests?logo=github">\n  </a>\n    <br>\n</p>\n\n<p align="center">\nA Python library/CLI tool for parsing Apple\'s <a href="https://www.theiphonewiki.com/wiki/IMG4_File_Format">Image4 format</a>.\n</p>\n\n## Usage\n```\nUsage: pyimg4 [OPTIONS] COMMAND [ARGS]...\n\n  A Python CLI tool for parsing Apple\'s Image4 format.\n\nOptions:\n  --version  Show the version and exit.\n  --help     Show this message and exit.\n\nCommands:\n  im4m  Image4 manifest commands\n  im4p  Image4 payload commands\n  im4r  Image4 restore info commands\n  img4  Image4 commands\n```\n\n## Requirements\n- Python 3.6 or higher (Python 3.7+ is recommended)\n- Python development headers (`python3-dev` on Debian-based OSes)\n\n## Installation\n- Install from [PyPI](https://pypi.org/project/pyimg4/):\n    - ```python3 -m pip install pyimg4```\n- Local installation:\n    - `./install.sh`\n    - Requires [Poetry](https://python-poetry.org)\n\n## TODO\n- Write documentation\n\n## Support\n\nFor any questions/issues you have, [open an issue](https://github.com/m1stadev/PyIMG4/issues) or join my [Discord](https://m1sta.xyz/discord).\n',
    'author': 'm1stadev',
    'author_email': 'adamhamdi31@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/m1stadev/PyIMG4',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
