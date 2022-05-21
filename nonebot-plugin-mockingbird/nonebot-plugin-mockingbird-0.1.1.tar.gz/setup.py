# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_mockingbird']

package_data = \
{'': ['*'], 'nonebot_plugin_mockingbird': ['resource/*']}

install_requires = \
['httpx>=0.22.0,<0.23.0',
 'langid>=1.1.0,<2.0.0',
 'mockingbirdforuse>=0.2.2,<0.3.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0b1,<3.0.0',
 'pydub>=0.25.0,<0.26.0']

setup_kwargs = {
    'name': 'nonebot-plugin-mockingbird',
    'version': '0.1.1',
    'description': '利用MockingBird生成语音并发送',
    'long_description': '## nonebot_plugin_mockingbird\n\n此项目灵感来源于 [Diaosi1111/nonebot_mockingbird_plugin](https://github.com/Diaosi1111/nonebot_mockingbird_plugin)\n\n### 食用方法\n\n**需要使用 python3.9**\n\n> 如果你的 python 版本为 3.8 则不可以食用\n\n1. 使用 nb-cli\n\n```shell\nnb plugin install nonebot_plugin_mockingbird\n```\n\n2. 使用 pip\n\n```shell\npip install nonebot_plugin_mockingbird\n```\n\n### 使用方法\n\n使用：\n\n```\n@Bot 说 [你想要bot说的话]\n```\n\n其他操作：\n\n```\n显示模型 # 显示出可供修改的模型\n# 修改指令\n修改模型 [序号]\\[模型名称]\n重载模型 进行模型重载(并没有什么卵用，或许以后内存泄漏解决会有用？)\n调整/修改精度 修改语音合成精度\n调整/修改句长 修改语音合成最大句长\n更新模型 更新模型列表\n```\n\n### 特别感谢\n\n- [Diaosi1111/nonebot_mockingbird_plugin](https://github.com/Diaosi1111/nonebot_mockingbird_plugin)\n- [babysor/MockingBird](https://github.com/babysor/MockingBird)\n- [HibiKier/zhenxun_bot](https://github.com/HibiKier/zhenxun_bot) 基于 Nonebot2 和 go-cqhttp 开发，以 postgresql 作为数据库，非常可爱的绪山真寻bot\n- [MeetWq/mybot](https://github.com/MeetWq/mybot)\n- [MeetWq/MockingBirdForUse](https://github.com/MeetWq/MockingBirdForUse)\n\n',
    'author': 'AkashiCoin',
    'author_email': 'l1040186796@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AkashiCoin/nonebot_plugin_mockingbird',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
