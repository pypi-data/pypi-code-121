# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot', 'nonebot.adapters.telegram']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0', 'nonebot2>=2.0.0b1,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-adapter-telegram',
    'version': '0.1.0b2',
    'description': 'Telegram Adapter for NoneBot2',
    'long_description': '<div align="center">\n\t<img width="200" src="docs/logo.png" alt="logo"></br>\n\n# NoneBot Adapter Telegram\n\n_✨ Telegram 协议适配 ✨_\n\n</div>\n\n## Manual\n\n[使用指南](./MANUAL.md)\n\n## TODO\n\n- [ ] Inline Mode Support\n- [x] Multiple Bot Support\n- [ ] All Event (with docstring)\n- [ ] All Method (with docstring)\n- [ ] All MessageSegment (with docstring)\n',
    'author': 'Jigsaw',
    'author_email': 'j1g5aw@foxmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://v2.nonebot.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
