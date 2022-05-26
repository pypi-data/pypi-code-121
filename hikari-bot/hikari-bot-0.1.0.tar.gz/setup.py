# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src\\plugins'}

packages = \
['hikari-bot']

package_data = \
{'': ['*'], 'hikari-bot': ['template/*']}

install_requires = \
['Jinja2>=3.0.0,<4.0.0',
 'httpx>=0.19.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-gocqhttp>=0.5.5,<0.6.0',
 'nonebot-plugin-htmlrender>=0.0.4',
 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'hikari-bot',
    'version': '0.1.0',
    'description': 'Nonebot2 HikariBot,支持战舰世界水表查询',
    'long_description': '# HikariBot\n战舰世界水表Bot，基于Nonebot2<br>\n水表人，出击！wws me recent！！！<br>\n如果觉得本插件还不错的话请点个Star哦~<br>\n[Hoshino版插件](https://github.com/benx1n/wows-stats-bot)\n## 特点\n\n- [x] 账号总体、单船、近期战绩\n- [x] 全指令支持参数乱序\n- [x] 快速切换绑定账号\n- [x] 支持@快速查询\n\n## 快速部署\n\n    ```\n    pip install nb-cli\n\n    ```\n\n## 感谢\n\n[Nonebot2](https://github.com/nonebot/nonebot2)<br>\n[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)<br>\n[战舰世界API平台](https://wows.linxun.link/)<br>\n\n## 开源协议\n\nMIT\n',
    'author': 'benx1n',
    'author_email': 'shirakamikanade@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/benx1n/HikariBot',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0',
}


setup(**setup_kwargs)
