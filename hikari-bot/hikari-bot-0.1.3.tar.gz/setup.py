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
    'version': '0.1.3',
    'description': 'Nonebot2 HikariBot,支持战舰世界水表查询',
    'long_description': '# HikariBot\n战舰世界水表Bot，基于Nonebot2<br>\n水表人，出击！wws me recent！！！<br>\n如果觉得本插件还不错的话请点个Star哦~<br>\n[Hoshino版插件](https://github.com/benx1n/wows-stats-bot)\n## 特点\n\n- [x] 账号总体、单船、近期战绩\n- [x] 全指令支持参数乱序\n- [x] 快速切换绑定账号\n- [x] 支持@快速查询\n\n## 快速部署（作为独立bot）\n1. 下载[notepad++](https://notepad-plus-plus.org/downloads/)和[Git](https://git-scm.com/download/win)并安装\n\n2. 下载[Python](https://www.python.org/downloads/windows/)版本需>3.8，或参考[Hoshino版插件](https://github.com/benx1n/wows-stats-bot)中使用Conda虚拟环境\n\n2. 执行下列两条命令安装nonebot2和hikari-bot插件\n    ```\n    pip install nb-cli\n    pip install hikari-bot\n    ```\n3. 打开一个合适的文件夹，鼠标右键——Git Bash here，输入以下命令克隆本Hoshino仓库\n    ```\n    git clone https://github.com/benx1n/HikariBot.git\n    cd HikariBot\n    ```\n4. 编辑.env.prod文件\n    ```\n    API_TOKEN = xxxxxxxx #无需引号\n    ```\n4. 运行bot\n    ```\n    nb run\n    ```\n    >此时若没有报错，您可以打开http://127.0.0.1:8080/go-cqhttp/\n    >\n    >点击左侧添加账号，重启bot即可在网页上看到相应信息（大概率需要扫码）\n\n## 快速部署（作为插件）\n1. 如果您已经有了一个基于Nonebot2的机器人（例如真寻），您可以直接\n    ```\n    pip install hikari-bot\n    ```\n2. 在bot的bot.py中加入\n    ```\n    nonebot.load_plugin(\'hikari_bot\')\n    ```\n3. 在环境文件中加入API_TOKEN = xxxxxxxxxxxx\n>一般来说该文件为.env.dev\n>\n>也有可能是.env.pord，具体需要看.env中是否有指定\n>\n>如果啥都不懂，bot.py里,在`nonebot.init()`下面加上\n>```\n>config = nonebot.get_driver().config\n>config.api_token = "xxxxxxxxxxxx"\n>```\n4. 重启bot\n\n## 更新\n\n```\npip install --upgrade hikari-bot\n(插件版无需下列两步)\ncd HikariBot\ngit pull\n```\n\n## 感谢\n\n[Nonebot2](https://github.com/nonebot/nonebot2)<br>\n[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)<br>\n[战舰世界API平台](https://wows.linxun.link/)<br>\n\n## 开源协议\n\nMIT\n',
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
