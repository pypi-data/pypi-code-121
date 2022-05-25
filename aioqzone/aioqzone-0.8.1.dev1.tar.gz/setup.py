# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aioqzone',
 'aioqzone.api',
 'aioqzone.interface',
 'aioqzone.type',
 'aioqzone.utils',
 'jssupport',
 'qqqr',
 'qqqr.qr',
 'qqqr.up',
 'qqqr.up.captcha']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'cssselect>=1.1.0,<2.0.0',
 'lxml>=4.8.0,<5.0.0',
 'opencv-python-headless>=4.5.5,<5.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'pytz>=2022.1,<2023.0',
 'rsa>=4.8,<5.0']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['numpy>=1.21.2,<1.22.0'],
 ':python_version >= "3.8" and python_version < "4.0"': ['numpy>=1.22.3,<2.0.0'],
 'dev': ['pre-commit>=2.17.0,<3.0.0',
         'black>=22.1.0,<23.0.0',
         'isort>=5.10.1,<6.0.0'],
 'doc': ['Sphinx>=4.5.0,<5.0.0',
         'autodoc-pydantic>=1.6.1,<2.0.0',
         'sphinx-autodoc-typehints<1.16.0',
         'sphinx-rtd-theme>=1.0.0,<2.0.0']}

setup_kwargs = {
    'name': 'aioqzone',
    'version': '0.8.1.dev1',
    'description': 'Python wrapper for Qzone web login and Qzone http api.',
    'long_description': '# aioqzone\n\naioqzone is a python package handling Qzone web login and wrapping some common Qzone Http apis.\n\n[![python](https://img.shields.io/pypi/pyversions/aioqzone?logo=python&logoColor=white)][home]\n[![QQQR](https://github.com/aioqzone/aioqzone/actions/workflows/qqqr.yml/badge.svg?branch=beta&event=schedule)](https://github.com/aioqzone/aioqzone/actions/workflows/qqqr.yml)\n[![version](https://img.shields.io/pypi/v/aioqzone?logo=python)][pypi]\n[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n[简体中文](https://github.com/aioqzone/aioqzone/blob/beta/README_zh-cn.md)\n\n## Features\n\n### Qzone Feature\n\n- [x] QR login\n- [x] password login (limited)\n- [ ] passing captcha (implemented but seems not working...)\n- [x] get complete html feeds\n- [x] get feed details\n- [x] get Qzone album\n- [x] like/unlike app\n- [x] publish/update/delete text feeds\n- [ ] comment\n\n### Why using this package?\n\n- [x] full ide typing support (typing)\n- [x] api response validation (pydantic)\n- [x] async design\n- [x] complete infrastructure to ease your own develop\n- [x] [doc support](https://aioqzone.github.io/aioqzone)\n\n__Working On:__\n\n- [ ] test coverage\n\n## Node Dependencies\n\n- `jssupport.jsjson.AstLoader` needn\'t outside processes.\n- To use `jssupport.execjs` and `jssupport.jsjson.NodeLoader`, you need to have `Node.js` installed (at least).\n- To use  `jssupport.jsdom`, you need to have npm packages `jsdom` and `canvas` to be installed.\n\n## Description\n\n|package    |brief description  |\n|-----------|-------------------|\n|aioqzone   |qzone api wrapper  |\n|jssupport  |communicate with node|\n|qqqr       |qzone web login    |\n\n## Examples\n\nYou can look for these repos for examples in practice.\n\n### aioqzone plugins\n\n- [aioqzone-feed][aioqzone-feed]: aioqzone plugin providing higher level api for processing feed\n\n\n## License\n\n```\nCopyright (C) 2022 aioqzone.\n\nThis program is free software: you can redistribute it and/or modify\nit under the terms of the GNU Affero General Public License as published\nby the Free Software Foundation, either version 3 of the License, or\n(at your option) any later version.\n\nThis program is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Affero General Public License for more details.\n\nYou should have received a copy of the GNU Affero General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/>.\n```\n\n- [AGPL-3.0](LICENSE)\n\n\n[home]: https://github.com/aioqzone/aioqzone "Python wrapper for Qzone web login and Qzone http api"\n[aioqzone-feed]: https://github.com/aioqzone/aioqzone-feed "aioqzone plugin providing higher level api for processing feed"\n[pypi]: https://pypi.org/project/aioqzone\n',
    'author': 'aioqzone',
    'author_email': 'zzzzss990315@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aioqzone/aioqzone',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
