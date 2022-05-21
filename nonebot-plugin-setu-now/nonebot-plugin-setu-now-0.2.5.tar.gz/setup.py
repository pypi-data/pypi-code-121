# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_setu_now']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.18.0,<1.0.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-apscheduler>=0.1.2,<0.2.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'pydantic>=1.5.0,<2.0.0',
 'webdav4>=0.9.3,<0.10.0']

setup_kwargs = {
    'name': 'nonebot-plugin-setu-now',
    'version': '0.2.5',
    'description': '另一个色图插件',
    'long_description': '# nonebot-plugin-setu-now\n\n- 另一个色图插件\n- 根据别人的改了亿点点\n- 现在可以色图保存到 `WebDAV` 服务器中来节省服务器空间(可选)\n- 采用**即时下载**并保存的方式来扩充*自己*图库(可选)\n- 支持私聊获取~~特殊~~色图\n- 对临时聊天不生效\n- 多个图在群聊中 > 3 图时合并发送 (不支持撤回)\n- 单个图逐个发送 (支持撤回)\n- CD 计算方式为: 设置的 CD 时间 \\* 获取图片的数量\n  - 如果设置了 60s 那么，\\*20 后就是 1200s = 2h\n\n## 安装配置\n\n```sh\npip install -U nonebot-plugin-setu-now\n```\n\n### .env 默认配置\n\n> 如果你不知道你要做什么 直接安装好插件 然后直接载入\n\n> 本章内容可以不看\n\n> 在吗？在读下去之前能不能告诉什么叫可选配备？\n\n是像这样写全都写上但是都留空吗？\n \n```ini\nsetu_cd=60\nsetu_save=\nsetu_path=\nsetu_porxy=\nsetu_reverse_proxy=\nsetu_dav_url=\nsetu_dav_username=\nsetu_dav_password=\nsetu_send_info_message=\nsetu_send_custom_message_path=\nsetu_withdraw=\nsetu_size=\nsetu_api_url=\nsetu_max=\n```\n\n很明显不是这个意思\n\n可选的意思是像这样：\n\n```ini\nsetu_cd=60\nsetu_save=local\nsetu_path=/data/setu\n```\n\n明白了吗？\n\n下面是配置的说明\n\n\n- `setu_cd` CD(单位秒) 可选 默认`60`秒\n- `setu_save` 保存模式 可选 `webdav`(保存到 webdav 服务器中) 或 `local`(本地) 或 留空,不保存\n- `setu_path` 保存路径 可选 当选择保存模式时可按需填写, 可不填使用默认\n  - webdav 可选 默认`/setu` `/setur18`\n  - 本地 可选 默认`./data/setu` `./data/setur18`\n- `setu_porxy` 代理地址 可选 当 pixiv 反向代理不能使用时可自定义\n- `setu_reverse_proxy` pixiv 反向代理 可选 默认 `i.pixiv.re`\n- webdav 设置 当选择保存保存模式为 `webdav` 时必须填写\n  - `setu_dav_username` 用户名\n  - `setu_dav_password` 密码\n  - `setu_dav_url` webdav 服务器地址\n- `setu_send_info_message` 是否发送图片信息 可选 默认 `ture` 填写 `false` 可关闭\n- `setu_send_custom_message_path` 自定义发送消息路径 可选 当填写路径时候开启 可以为相对路径\n  - 文件应该为 `json` 格式如下\n  - 可在 `setu_message_cd` 中添加 `{cd_msg}` 提示 CD 时间\n  ```json\n  {\n    "send": ["abc"],\n    "cd": ["cba cd: {cd_msg}"]\n  }\n  ```\n- `setu_withdraw` 撤回发送的色图消息的时间, 单位: 秒 可选 默认`关闭` 填入数字来启用, 建议 `10` ~ `120` **仅对于非合并转发使用**\n- `setu_size` 色图质量 默认 `regular` 可选 `original` `regular` `small` `thumb` `mini`\n- `setu_api_url` 色图信息 api 地址 默认`https://api.lolicon.app/setu/v2` 如果有 api 符合类型也能用\n- `setu_max` 一次获取色图的数量 默认 `30` 如果你的服务器/主机内存吃紧 建议调小\n`\n~~所有配置都可选了,还能出问题吗?~~\n\n\n那你可以告诉我，下面这个设置出现了什么问题吗？\n\n```ini\nsetu_send_custom_message_path={\n    "send": ["abc"],\n    "cd": ["cba cd: {cd_msg}"]\n  }\nsetu_porxy=127.0.0。1:1234\nsetu_reverse_proxy=\nsetu_max=0\n```\n\n## 载入插件 bot.py\n\n```py\nnonebot.load_plugin("nonebot_plugin_setu_now")\n```\n\n## 使用\n\n如果你能读懂正则就不用看了\n\n```r\n^(setu|色图|涩图|来点色色|色色|涩涩|来点色图)\\s?([x]?\\d+[张|个|份]?)?\\s?(r18)?\\s?\\s?(tag)?\\s?(.*)?\n```\n\n- 指令 以 `setu|色图|涩图|来点色色|色色|涩涩` 为开始\n  - 然后接上可选数量 `x10` `10张|个|份`\n  - 再接上可选 `r18`\n  - 可选 `tag`\n  - 最后是关键词\n- 说明\n  - 数量 可选 默认为 1\n  - `r18` 可选 仅在私聊可用 群聊直接忽视\n  - `tag` 可选 如有 关键词参数会匹配 `pixiv 标签 tag`\n  - 关键词 可选 匹配任何 `标题` `作者` 或 `pixiv 标签`\n- 例子\n  - `来点色色 妹妹`\n  - `setur18`\n  - `色图 x20 tag 碧蓝航线 妹妹`\n  - `涩涩10份魅魔`\n\n# 在吗？\n\n- 这个是 `on_regex` 而不是 `on_commend`\n- 本插件一般都经过测试后才发版，如果遇到了任何问题，请先自行解决\n- 任何`不正确使用插件`的 issue 将会直接关闭\n',
    'author': 'kexue',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kexue-z/nonebot-plugin-setu-now',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
