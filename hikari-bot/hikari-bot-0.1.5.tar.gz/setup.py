# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src\\plugins'}

packages = \
['hikari_bot']

package_data = \
{'': ['*'], 'hikari_bot': ['template/*']}

install_requires = \
['Jinja2>=3.0.0,<4.0.0',
 'httpx>=0.19.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-apscheduler>=0.1.2,<0.2.0',
 'nonebot-plugin-gocqhttp>=0.5.5,<0.6.0',
 'nonebot-plugin-htmlrender>=0.0.4',
 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'hikari-bot',
    'version': '0.1.5',
    'description': 'Nonebot2 HikariBot,支持战舰世界水表查询',
    'long_description': '<!-- markdownlint-disable MD033 MD041 -->\n<p align="center">\n  <a href="https://github.com/benx1n/HikariBot"><img src="https://s2.loli.net/2022/05/27/6lsND3dA5GxQjMg.png" alt="Hikari " style="width:200px; height:200px; border-radius:100%" ></a>\n</p>\n\n<div align="center">\n\n# Hikari\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n战舰世界水表BOT\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  <a href="https://github.com/benx1n/HikariBot">\n    <img src="https://img.shields.io/github/license/benx1n/HikariBot" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/hikari-bot">\n    <img src="https://img.shields.io/pypi/v/hikari-bot" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.8.0+-blue" alt="python">\n  <a href="https://jq.qq.com/?_wv=1027&k=S2WcTKi5">\n    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-967546463-orange?style=flat-square" alt="QQ Chat Group">\n  </a>\n</p>\n\n## 简介\n\n战舰世界水表BOT，基于Nonebot2<br>\n水表人，出击！wws me recent！！！<br>\n如果觉得本插件还不错的话请点个Star哦~<br>\n[Hoshino版插件](https://github.com/benx1n/wows-stats-bot)\n\n## 特色\n\n- [x] 账号总体、单船、近期战绩\n- [x] 全指令支持参数乱序\n- [x] 快速切换绑定账号\n- [x] 支持@快速查询\n\n## 快速部署（作为独立bot）\n1. 下载[notepad++](https://notepad-plus-plus.org/downloads/)、[Git](https://git-scm.com/download/win)、[Python](https://www.python.org/downloads/windows/)并安装\n    >Python版本需>3.8，或参考[Hoshino版插件](https://github.com/benx1n/wows-stats-bot)中使用Conda虚拟环境\n\n3. 打开一个合适的文件夹，鼠标右键——Git Bash here，输入以下命令克隆本Hoshino仓库\n   > ```\n   > git clone https://github.com/benx1n/HikariBot.git\n   > ```\n3. 双击`一键安装.bat` \n\n   >执行下列两条命令安装nonebot2和hikari-bot插件\n   > ```\n   > pip install nb-cli\n   > pip install hikari-bot\n   > ```\n   >\n4. 编辑.env.prod文件\n   > ```\n   > API_TOKEN = xxxxxxxx #无需引号，格式为您的KEY:TOKEN,半角冒号相连\n   >SUPERUSERS=["QQ号"] \n   > ```\n\n5. 双击`启动.bat`\n    >打开终端，进入HikariBot文件夹下，输入下方命令运行bot\n    >```\n    >nb run\n    >```\n    >此时若没有报错，您可以打开http://127.0.0.1:8080/go-cqhttp/\n    >\n    >点击左侧添加账号，重启bot即可在网页上看到相应信息（大概率需要扫码）\n\n## 快速部署（作为插件）\n1. 如果您已经有了一个基于Nonebot2的机器人（例如真寻），您可以直接\n    ```\n    pip install hikari-bot\n    ```\n2. 在bot的bot.py中加入\n    ```\n    nonebot.load_plugin(\'hikari_bot\')\n    ```\n3. 在环境文件中加入\n    ```\n    API_TOKEN = xxxxxxxxxxxx\n    SUPERUSERS=["QQ号"] \n    ```\n>一般来说该文件为.env.dev\n>\n>也有可能是.env.pord，具体需要看.env中是否有指定\n>\n>如果啥都不懂，bot.py里,在`nonebot.init()`下面加上\n>```\n>config = nonebot.get_driver().config\n>config.api_token = "xxxxxxxxxxxx"\n>```\n>请点击页面顶部链接加群获取Token哦~\n>\n4. 重启bot\n\n## 更新\n双击`更新.bat`\n\n>```\n>pip install --upgrade hikari-bot\n>```\n>install结束后会打印当前版本\n>\n>您也可以通过pip show hikari-bot查看\n>\n>如果没有更新到最新版请等待一会儿，镜像站一般每五分钟同步\n>\n>(插件版无需下列两步)\n>```\n>cd HikariBot\n>\n>git pull\n>```\n## 感谢\n\n[Nonebot2](https://github.com/nonebot/nonebot2)<br>\n[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)<br>\n[战舰世界API平台](https://wows.linxun.link/)<br>\n\n## 开源协议\n\nMIT\n',
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
