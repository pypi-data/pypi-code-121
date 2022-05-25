# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hardwario', 'hardwario.chester', 'hardwario.chester.cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'docker>=5.0.3,<6.0.0',
 'hardwario-common>=1.6.1,<2.0.0',
 'loguru>=0.6.0,<0.7.0',
 'prompt-toolkit>=3.0.28,<4.0.0',
 'pylink-square>=0.12.0,<0.13.0',
 'pynrfjprog==10.15.2',
 'pyperclip>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['chester = hardwario.chester.cli:main']}

setup_kwargs = {
    'name': 'hardwario-chester',
    'version': '1.10.0',
    'description': 'HARDWARIO CHESTER',
    'long_description': '<a href="https://www.hardwario.com/"><img src="https://www.hardwario.com/ci/assets/hw-logo.svg" width="200" alt="HARDWARIO Logo" align="right"></a>\n\n# HARDWARIO CHESTER CLI Tools\n\n[![Main](https://github.com/hardwario/py-hardwario-chester/actions/workflows/main.yaml/badge.svg)](https://github.com/hardwario/py-hardwario-chester/actions/workflows/main.yaml)\n[![Release](https://img.shields.io/github/release/hardwario/py-hardwario-chester.svg)](https://github.com/hardwario/py-hardwario-chester/releases)\n[![PyPI](https://img.shields.io/pypi/v/hardwario-chester.svg)](https://pypi.org/project/hardwario-chester/)\n[![License](https://img.shields.io/github/license/hardwario/py-hardwario-chester.svg)](https://github.com/hardwario/py-hardwario-chester/blob/master/LICENSE)\n[![Twitter](https://img.shields.io/twitter/follow/hardwario_en.svg?style=social&label=Follow)](https://twitter.com/hardwario_en)\n\nThis repository contains Python package [hardwario-chester](https://pypi.org/project/hardwario-chester/)\n\n\n## License\n\nThis project is licensed under the [MIT License](https://opensource.org/licenses/MIT/) - see the [LICENSE](LICENSE) file for details.\n\n---\n\nMade with &#x2764;&nbsp; by [**HARDWARIO s.r.o.**](https://www.hardwario.com/) in the heart of Europe.\n',
    'author': 'Karel Blavka',
    'author_email': 'karel.blavka@hardwario.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hardwario/py-hardwario-chester',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2',
}


setup(**setup_kwargs)
