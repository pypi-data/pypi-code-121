# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_word_bank2']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0',
 'httpx>=0.18.0,<1.0.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1',
 'nonebot2>=2.0.0-beta.2']

setup_kwargs = {
    'name': 'nonebot-plugin-word-bank2',
    'version': '0.1.5.5',
    'description': '无数据问答插件',
    'long_description': '<div align="center">\n\n# nonebot-plugin-word-bank2\n\n_✨ 无数据库的轻量问答插件 ✨_\n\n</div>\n\n\n# 功能\n\n- 无数据库的轻量问答插件\n- 支持模糊问答\n- 支持特殊回复\n- 自动转译CQ码\n- 支持图片回复\n- 支持指令大杂烩\n\n# 安装\n\n```\npip install nonebot-plugin-word-bank2\n```\n\n\n# 开始使用\n\n## 问答教学\n\n- 设置词条命令由`问句`和`答句`组成。设置之后,  收到`消息`时触发。并非所有人都可以设置词条,  详见[权限](#permission)\n\n- 格式`[模糊|全局|正则|@]问...答...`\n  - `模糊|正则` 匹配模式中可任性一个或`不选`, `不选` 表示 `全匹配`\n  - `全局`, `@` 可与以上匹配模式组合使用\n\n- 教学中可以使用换行\n  - 例如\n    ```\n    问\n    123\n    答\n    456\n    ```\n\n- 问答句中的首首尾空白字符会被自动忽略\n\n- 私聊好友个人也可以建立属于自己的词库, 可以实现类似备忘录的功能\n\n### 问句选项\n\n- `问...答...` 全匹配模式, 必须全等才能触发答\n\n\n- `模糊问...答...` 当`问句`出现在`消息`里时则会触发\n\n\n- `正则问...答...`,  当`问句`被`消息`正则捕获时则会匹配\n-\n    例如: 正则问[他你]不理答你被屏蔽了\n\n    | 消息     | 回复       |\n    | -------- | ---------- |\n    | 他不理   | 你被屏蔽了 |\n    | 他不理我 | 你被屏蔽了 |\n    | 你不理我 | 你被屏蔽了 |\n\n\n- `全局问...答...`,  在所有群聊和私聊中都可以触发,  可以和以上几种组合使用\n  - 例如: `全局模糊问 晚安 答 不准睡`\n\n\n- `@问...答...`,  只有 `event.tome` 时才会触发，如被@、被回复时或在私聊中，可以和以上几种组合使用\n  - 例如: `全局模糊@问 晚安 答 不准睡`\n\n\n- 问句可包含`at` 即在QQ聊天中手动at群友\n  - 建议只在`问...答...`中使用\n  - 例如: `问 @这是群名称 答 老婆!`\n\n\n###  答句选项\n\n- `/at` + `qq号`, 当答句中包含`/at` + `qq号`时将会被替换为@某人\n  - 例如: `问 群主在吗 答 /at 123456789在吗`\n\n- `/self`, 当答句中包含`/self`时将会被替换为发送者的群昵称\n  - 例如: `问 我是谁 答 你是/self` (群昵称为: 我老婆)\n\n- `/atself`, 当答句中包含`/atself`时将会被替换为@发送者\n  - 例如: `问 谁是牛头人 答 @这是群昵称`\n\n\n## 删除词条\n\n- `删除[模糊|全局|正则|@]词条` + 需要删除的`问句`\n  - 例如: `删除全局模糊@词条 你好`\n\n\n- 以下指令需要结合自己的`COMMAND_START` 这里为 `/`\n\n- 删除词库: 删除当前群聊/私聊词库\n  - 例如: `/删除词库`\n\n- 删除全局词库\n  - 例如: `/删除全局词库`\n\n- 删除全部词库\n  - 例如: `/删除全部词库`\n\n- <span id="permission">权限</span>\n\n|              | 群主 | 群管理 | 私聊好友 | 超级用户 |\n| ------------ | ---- | ------ | -------- | -------- |\n| 增删词条     | O    | O      | O        | O        |\n| 增删全局词条 | X    | X      | X        | O        |\n| 删除词库     | O    | O      | O        | O        |\n| 删除全局词库 | X    | X      | X        | O        |\n| 删除全部词库 | X    | X      | X        | O        |\n\n\n# 特别感谢\n\n- [Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp)\n- [nonebot/nonebot2](https://github.com/nonebot/nonebot2)\n- [Joenothing-lst/word-bank](https://github.com/Joenothing-lst/word-bank)\n- [MeetWq](https://github.com/MeetWq)\n\n# 优化建议\n\n- 请提交issue或者pr\n',
    'author': 'kexue',
    'author_email': 'x@kexue.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kexue-z/nonebot-plugin-word-bank2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
