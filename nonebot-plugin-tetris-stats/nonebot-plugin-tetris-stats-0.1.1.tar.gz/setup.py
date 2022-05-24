# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_tetris_stats']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'asyncio>=3.4.3,<4.0.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-beta.3,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-tetris-stats',
    'version': '0.1.1',
    'description': '一个基于nonebot2的用于查询TETRIS相关游戏玩家数据的插件',
    'long_description': 'TETRIS Stats\n============\n\n一个基于nonebot2的用于查询TETRIS相关游戏玩家数据的插件  \n目前支持\n* [TETR.IO](https://tetr.io/)\n* [茶服](https://teatube.cn/tos/)\n\n计划支持\n* [TOP](http://tetrisonline.pl/)\n\n安装\n----\n\n* 使用 pip\n\n```\npip install nonebot-plugin-tetris-stats\n```\n\n使用\n----\n\n参考NoneBot2文档 [加载插件](https://v2.nonebot.dev/docs/tutorial/plugin/load-plugin/)\n\n依赖\n----\n\n目前只支持 `OneBot V11` 协议\n\n鸣谢\n----\n\n* [NoneBot2](https://v2.nonebot.dev/)\n* [OneBot](https://onebot.dev/)\n* [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/)\n\n开源\n----\n\n本项目使用[MIT](https://github.com/shoucandanghehe/nonebot-plugin-tetris-stats/blob/main/LICENSE)许可证开源\n',
    'author': 'scdhh',
    'author_email': 'wallfjjd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/shoucandanghehe/nonebot-plugin-tetris-stats',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
