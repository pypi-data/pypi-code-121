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
 'beautifulsoup4>=4.11.1,<5.0.0',
 'httpx>=0.19.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-apscheduler>=0.1.2,<0.2.0',
 'nonebot-plugin-gocqhttp>=0.5.5,<0.6.0',
 'nonebot-plugin-htmlrender>=0.0.4',
 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'hikari-bot',
    'version': '0.1.8',
    'description': 'Nonebot2 HikariBot,支持战舰世界水表查询',
    'long_description': '<!-- markdownlint-disable MD033 MD041 -->\n<p align="center">\n  <a href="https://github.com/benx1n/HikariBot"><img src="https://s2.loli.net/2022/05/28/SFsER8m6TL7jwJ2.png" alt="Hikari " style="width:200px; height:200px" ></a>\n</p>\n\n<div align="center">\n\n# Hikari\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n战舰世界水表BOT\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  <a href="https://pypi.python.org/pypi/hikari-bot">\n    <img src="https://img.shields.io/pypi/v/hikari-bot" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.8.0+-blue" alt="python">\n  <a href="https://jq.qq.com/?_wv=1027&k=S2WcTKi5">\n    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-967546463-orange?style=flat-square" alt="QQ Chat Group">\n  </a>\n</p>\n\n## 简介\n\n战舰世界水表BOT，基于Nonebot2<br>\n水表人，出击！wws me recent！！！<br>\n如果觉得本插件还不错的话请点个Star哦~<br>\n[Hoshino版插件](https://github.com/benx1n/wows-stats-bot)\n\n## 特色\n\n- [x] 账号总体、单船、近期战绩\n- [x] 全指令支持参数乱序\n- [x] 快速切换绑定账号\n- [x] 支持@快速查询\n\n## 快速部署（作为独立bot）\n[视频教程](https://www.bilibili.com/video/BV1r5411X7pr)\n1. 下载[notepad++](https://notepad-plus-plus.org/downloads/)、[Git](https://git-scm.com/download/win)、[Python](https://www.python.org/downloads/windows/)并安装\n    >Python版本需>3.8，或参考[Hoshino版插件](https://github.com/benx1n/wows-stats-bot)中使用Conda虚拟环境\n    >\n    >请注意python安装时勾选或点击`添加到环境变量`，可以安装后cmd中输入`python --version`来验证是否成功\n    >\n    >否则请自行百度如何添加python到环境变量\n\n3. 打开一个合适的文件夹，鼠标右键——Git Bash here，输入以下命令（任选一条）克隆本Hikari仓库\n   > ```\n   > git clone https://github.com/benx1n/HikariBot.git\n   >\n   > git clone https://gitee.com/benx1n/HikariBot.git\n   > ```\n3. 双击`一键安装.bat` \n\n   >执行下列两条命令安装nonebot2和hikari-bot插件\n   > ```\n   > pip install nb-cli\n   > pip install hikari-bot\n   > ```\n   >\n4. 编辑.env.prod文件\n   > ```\n   > API_TOKEN = xxxxxxxx #无需引号，格式为您的KEY:TOKEN,半角冒号相连,KEY即您申请TOKEN时使用的QQ号，TOKEN即回复您的邮件\n   >SUPERUSERS=["QQ号"] \n   > ```\n   >总之最后应该长这样\n   >\n   >API_TOKEN = 123764323:ba1f2511fc30423bdbb183fe33\n\n5. 双击`启动.bat`，在打开的浏览器中添加bot账号密码，重新启动Hikari\n    >打开终端，进入HikariBot文件夹下，输入下方命令运行bot\n    >```\n    >nb run\n    >```\n    >此时若没有报错，您可以打开http://127.0.0.1:8080/go-cqhttp/\n    >\n    >点击左侧添加账号，重启bot即可在网页上看到相应信息（大概率需要扫码）\n    >\n    >如果重启后go-cqhhtp一直卡在扫码或无限重启，请继续往下阅读\n\n\n## 快速部署（作为插件）\n1. 如果您已经有了一个基于Nonebot2的机器人（例如真寻），您可以直接\n    ```\n    pip install hikari-bot\n    ```\n2. 在bot的bot.py中加入\n    ```\n    nonebot.load_plugin(\'hikari_bot\')\n    ```\n3. 在环境文件中加入\n    ```\n    API_TOKEN = xxxxxxxxxxxx\n    SUPERUSERS=["QQ号"] \n    ```\n>一般来说该文件为.env.dev\n>\n>也有可能是.env.pord，具体需要看.env中是否有指定\n>\n>如果啥都不懂，bot.py里,在`nonebot.init()`下面加上\n>```\n>config = nonebot.get_driver().config\n>config.api_token = "xxxxxxxxxxxx"\n>```\n>请点击页面顶部链接加群获取Token哦~\n>\n4. 重启bot\n\n## 更新\n双击`更新.bat`\n\n>```\n>pip install --upgrade hikari-bot\n>```\n>install结束后会打印当前版本\n>\n>您也可以通过pip show hikari-bot查看\n>\n>如果没有更新到最新版请等待一会儿，镜像站一般每五分钟同步\n>\n>(插件版无需下列步骤，Bot版在更新说明中没有提到git pull也不需要)\n>```\n>cd HikariBot\n>\n>git fetch --all\n>\n>git reset --hard origin/master\n>\n>git pull\n>```\n>\n>重新编辑您的.env.prod文件\n>\n>(如果您会自己解决分支冲突不看也可以.jpg\n\n## 可能会遇到的问题\n\n### 无法使用内嵌go-cqhttp登录bot\n\n1. 下载 go-cqhttp 至合适的文件夹\n\n    - github 发布页：https://github.com/Mrs4s/go-cqhttp/releases\n\n    > 您需要根据自己的机器架构选择版本，Windows一般为x86/64架构，通常选择[go-cqhttp_windows_386.exe](https://github.com/Mrs4s/go-cqhttp/releases/download/v1.0.0-rc1/go-cqhttp_windows_386.exe)\n\n2. 双击go-cqhttp，提示释出bat，重新运行bat，选择websocket反向代理，go-cqhttp将会在同文件夹内自动创建一个`config.yml`，右键使用notepad++打开，根据注释填写QQ账号密码，并将以下内容写入文件结尾：\n\n    ```yaml\n      - ws-reverse:\n          universal: ws://127.0.0.1:8080/onebot/v11/ws\n          reconnect-interval: 5000\n          middlewares:\n            <<: *default\n    ```\n    \n    > 关于go-cqhttp的配置，你可以在[这里](https://docs.go-cqhttp.org/guide/config.html#%E9%85%8D%E7%BD%AE%E4%BF%A1%E6%81%AF)找到更多说明。\n\n3. 启动go-cqhttp，按照提示登录。\n\n\n4. 修改Hikari文件夹下.env.prod中`USE_PLUGIN_GO_CQHTTP`的值为`false`\n    ```\n    USE_PLUGIN_GO_CQHTTP = false\n    ```\n5. 在文件夹下打开终端，输入`nb run`启动bot\n\n### 外置go-cqhttp也无法登录\n>一般提示需要扫码，扫码后提示异地无法登录\n>\n>关于该问题，您可以查看[#1469](https://github.com/Mrs4s/go-cqhttp/issues/1469)获得相应解决办法\n## 感谢\n\n[Nonebot2](https://github.com/nonebot/nonebot2)<br>\n[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)<br>\n[战舰世界API平台](https://wows.linxun.link/)<br>\n\n## 开源协议\n\nMIT\n',
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
