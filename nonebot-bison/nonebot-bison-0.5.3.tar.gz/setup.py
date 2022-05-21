# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src/plugins'}

packages = \
['nonebot_bison', 'nonebot_bison.admin_page', 'nonebot_bison.platform']

package_data = \
{'': ['*'],
 'nonebot_bison.admin_page': ['dist/*',
                              'dist/static/css/*',
                              'dist/static/js/*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0',
 'apscheduler>=3.7.0,<4.0.0',
 'bs4>=0.0.1,<0.0.2',
 'expiringdict>=1.2.1,<2.0.0',
 'feedparser>=6.0.2,<7.0.0',
 'httpx>=0.16.1',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-htmlrender>=0.0.4,<0.0.5',
 'nonebot2>=2.0.0-beta.2,<3.0.0',
 'pillow>=8.1,<10.0',
 'pyjwt>=2.1.0,<3.0.0',
 'python-socketio>=5.4.0,<6.0.0',
 'tinydb>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'nonebot-bison',
    'version': '0.5.3',
    'description': 'Subscribe message from social medias',
    'long_description': '<div align="center">\n<h1>Bison </br>通用订阅推送插件</h1>\n\n[![pypi](https://badgen.net/pypi/v/nonebot-bison)](https://pypi.org/project/nonebot-bison/)\n[![license](https://img.shields.io/github/license/felinae98/nonebot-bison)](https://github.com/felinae98/nonebot-bison/blob/main/LICENSE)\n[![felinae98](https://circleci.com/gh/felinae98/nonebot-bison.svg?style=shield)](https://circleci.com/gh/felinae98/nonebot-bison)\n[![docker](https://img.shields.io/docker/image-size/felinae98/nonebot-bison)](https://hub.docker.com/r/felinae98/nonebot-bison)\n[![codecov](https://codecov.io/gh/felinae98/nonebot-bison/branch/main/graph/badge.svg?token=QCFIODJOOA)](https://codecov.io/gh/felinae98/nonebot-bison)\n[![qq group](https://img.shields.io/badge/QQ%E7%BE%A4-868610060-orange)](https://qm.qq.com/cgi-bin/qm/qr?k=pXYMGB_e8b6so3QTqgeV6lkKDtEeYE4f&jump_from=webapi)\n\n[文档](https://nonebot-bison.vercel.app)|[开发文档](https://nonebot-bison.vercel.app/dev)\n\n</div>\n\n## 简介\n\n一款自动爬取各种站点，社交平台更新动态，并将信息推送到 QQ 的机器人。\n基于 [`NoneBot2`](https://github.com/nonebot/nonebot2) 开发（诞生于明日方舟的蹲饼活动）\n\n<details>\n<summary>本项目原名原名nonebot-hk-reporter</summary>\n\n寓意本 Bot 要做全世界跑的最快的搬运机器人，后因名字过于暴力改名\n\n</details>\n本项目名称来源于明日方舟角色拜松——一名龙门的信使，曾经骑自行车追上骑摩托车的德克萨斯\n\n支持的平台：\n\n- 微博\n  - 图文\n  - 视频\n  - 纯文字\n  - 转发\n- Bilibili\n  - 视频\n  - 图文\n  - 专栏\n  - 转发\n  - 纯文字\n- RSS\n  - 富文本转换为纯文本\n  - 提取出所有图片\n- 明日方舟\n  - 塞壬唱片新闻\n  - 游戏内公告\n  - 版本更新等通知\n  - 泰拉记事社漫画\n- 网易云音乐\n  - 歌手发布新专辑\n  - 电台更新\n- FF14\n  - 游戏公告\n\n## 功能\n\n- 定时爬取指定网站\n- 通过图片发送文本，防止风控\n- 使用队列限制发送频率\n- 使用网页后台管理 Bot 订阅\n\n## 使用方法\n\n**!!注意，如果要使用后台管理功能请使用 pypi 版本或者 docker 版本，如果直接 clone 源代码\n需要按下面方式进行 build**\n\n```bash\ncd ./admin-frontend\nyarn && yarn build\n```\n\n可以使用 Docker，docker-compose，作为插件安装在 nonebot 中，或者直接运行  \n参考[文档](https://nonebot-bison.vercel.app/usage/#%E4%BD%BF%E7%94%A8)\n\n## FAQ\n\n1. 报错`TypeError: \'type\' object is not subscriptable`  \n   本项目使用了 Python 3.9 的语法，请将 Python 版本升级到 3.9 及以上，推荐使用 docker 部署\n2. bot 不理我  \n   请确认自己是群主或者管理员，并且检查`COMMAND_START`环境变量是否设为`[""]`\n   或者按照`COMMAND_START`中的设置添加命令前缀，例：\n   `COMMAND_START=["/"]`则应发送`/添加订阅`\n3. 微博漏订阅了\n   微博更新了新的风控措施，某些含有某些关键词的微博会获取不到。\n4. 无法使用后台管理页面\n   1. 确认自己正确配置了 nonebot 的端口，如果在远程或容器外访问网页请确保`HOST=0.0.0.0`\n   2. 确认自己的云服务器的防火墙配置正确\n   3. 确认自己使用了正确的方法安装插件\n\n## 参与开发\n\n欢迎各种 PR，参与开发本插件很简单，只需要对相应平台完成几个接口的编写就行。你只需要一点简单的爬虫知识就行。\n\n如果对整体框架有任何意见或者建议，欢迎 issue。\n\n## 鸣谢\n\n- [`go-cqhttp`](https://github.com/Mrs4s/go-cqhttp)：简单又完善的 cqhttp 实现\n- [`NoneBot2`](https://github.com/nonebot/nonebot2)：超好用的开发框架\n- [`HarukaBot`](https://github.com/SK-415/HarukaBot/): 借鉴了大体的实现思路\n- [`rsshub`](https://github.com/DIYgod/RSSHub)：提供了大量的 api\n\n## License\n\nMIT\n',
    'author': 'felinae98',
    'author_email': 'felinae225@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/felinae98/nonebot-bison',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
