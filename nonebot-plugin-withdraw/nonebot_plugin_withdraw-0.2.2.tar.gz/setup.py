# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_withdraw']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0', 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-withdraw',
    'version': '0.2.2',
    'description': 'A simple withdraw plugin for Nonebot2',
    'long_description': '# nonebot-plugin-withdraw\n\n基于 [nonebot2](https://github.com/nonebot/nonebot2) 的简单撤回插件，让机器人撤回 **自己发出的消息**\n\n使用场景是如果机器人发出了不和谐的消息，群友可以帮忙及时撤回\n\n注意如果机器人不是管理员，则无法撤回2分钟以上的消息\n\n\n### 使用\n\n**以下命令需要加[命令前缀](https://v2.nonebot.dev/docs/api/config#Config-command_start) (默认为`/`)，可自行设置为空**\n\n#### 方式1：\n\n`@机器人 撤回 [num1][-num2]`\n\n*注：若命令前缀为空则需要 @机器人，否则可不@*\n\n`num` 指机器人发的倒数第几条消息，从 `0` 开始，默认为 `0`\n\n`num`不需要加`[]`，仅为了说明是可选参数\n\n示例：\n\n```\n@机器人 撤回    # 撤回倒数第一条消息\n@机器人 撤回 1    # 撤回倒数第二条消息\n@机器人 撤回 0-3    # 撤回倒数三条消息\n```\n\n#### 方式2：\n\n回复需要撤回的消息，回复“撤回”\n',
    'author': 'meetwq',
    'author_email': 'meetwq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MeetWq/nonebot-plugin-withdraw',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
