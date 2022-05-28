# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot', 'nonebot.adapters.feishu']

package_data = \
{'': ['*']}

install_requires = \
['cashews>=4.0.0,<5.0.0',
 'httpx>=0.18.0,<1.0.0',
 'nonebot2>=2.0.0-beta.1',
 'pycryptodome>=3.10.1,<4.0.0']

setup_kwargs = {
    'name': 'nonebot-adapter-feishu',
    'version': '2.0.0b3',
    'description': 'feishu(larksuite) adapter for nonebot2',
    'long_description': '<p align="center">\n  <a href="https://feishu.adapters.nonebot.dev/"><img src="https://feishu.adapters.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# NoneBot-Adapter-Feishu\n\n_✨ 飞书协议适配 ✨_\n\n</div>\n',
    'author': 'StarHeartHunt',
    'author_email': 'starheart233@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://feishu.adapters.nonebot.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
