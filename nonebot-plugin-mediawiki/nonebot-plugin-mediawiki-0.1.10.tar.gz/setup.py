# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_mediawiki']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4.post0',
 'nonebot-adapter-onebot>=2.0.0b1,<2.1.0',
 'nonebot2>=2.0.0b3,<2.1.0']

setup_kwargs = {
    'name': 'nonebot-plugin-mediawiki',
    'version': '0.1.10',
    'description': 'nonebot2 mediawiki 查询插件',
    'long_description': '<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# nonebot-plugin-mediawiki\n\n_适用于 [NoneBot2](https://v2.nonebot.dev) 的 MediaWiki 查询插件_\n\n</div>\n\n------\n\n<div align="center">\n\n![Python](https://img.shields.io/badge/python-3.8%2B-lightgrey)\n![nonebot2](https://img.shields.io/badge/nonebot2-2.0.0b2-yellowgreen)\n[![GitHub license](https://img.shields.io/github/license/KoishiMoe/nonebot-plugin-mediawiki)](https://github.com/KoishiMoe/nonebot-plugin-mediawiki/blob/main/LICENSE)\n[![pypi](https://img.shields.io/pypi/v/nonebot-plugin-mediawiki?color=blue)](https://pypi.org/project/nonebot-plugin-mediawiki/)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/nonebot-plugin-mediawiki)\n\n[![GitHub issues](https://img.shields.io/github/issues/KoishiMoe/nonebot-plugin-mediawiki)](https://github.com/KoishiMoe/nonebot-plugin-mediawiki/issues)\n[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/KoishiMoe/nonebot-plugin-mediawiki?include_prereleases)](https://github.com/KoishiMoe/nonebot-plugin-mediawiki/releases)\n![GitHub contributors](https://img.shields.io/github/contributors/KoishiMoe/nonebot-plugin-mediawiki)\n![GitHub Repo stars](https://img.shields.io/github/stars/KoishiMoe/nonebot-plugin-mediawiki?style=social)\n\n</div>\n\n------\n\n本项目是 [Flandre](https://github.com/KoishiMoe/Flandre) 的\n[wiki](https://github.com/KoishiMoe/Flandre/tree/main/src/plugins/wiki) 组件，经简单修改成为独立插件发布\n\n## 用途\n一般来说最需要wikibot的大概是一些wiki项目的交流群，不过鉴于这种群通常都有大佬在，写个bot自然不是什么难事的说～\n所以我在本插件开发时更注重于在一般的群聊中能起作用的功能，供交流问题时快速引用。例如游戏的交流群，可能需要经常在wiki上查找角色信息、游戏特性等，\n去wiki上手动翻链接显然很麻烦。同时，对很多群来说，交流的话题都很广泛，例如今天聊mc明天聊泰拉后天聊战地等情况都是存在的，\n因此我着重设计了对多个wiki的支持。而对一些更加专业的、wiki项目的群才能用到的功能（例如页面更改提醒），则不在开发计划中。当然，如果没有这些需求，\n本插件也适合wiki项目的群使用，例如本插件具有的完善的全局管理与回落机制，可以降低群管理人员在管理同一项目的群时的成本，等等。\n\n啊啦，说了这么多，总而言之，欢迎使用！欢迎提交issue！（如果有pr就更好了～）\n\n## 使用说明\n\n### TL;DR\n\n查询条目： `[[条目名]]` `[[prefix:条目名]]`\n\n查询条目（方法2）： `wiki 条目名` `wiki prefix:条目名`\n\n查询模板： `{{模板名}}` `{{prefix:模板名}}`\n\n绕过api查询条目： `((条目名))` `((prefix:条目名))`\n\n添加（全局）Wiki： `wiki.add` `wiki.add.global`\n\n删除（全局）Wiki： `wiki.delete` `wiki.delete.global`\n\n修改（全局）默认Wiki： `wiki.default` `wiki.default.global`\n\n查看Wiki列表： `wiki.list` `wiki.list.global`\n\n**其中所有非全局指令均需要在目标群中进行，所有全局指令均只有Bot管理员能执行**\n\n### 查询功能\n\n查询功能的语法和标准的mediawiki内链格式基本一致：\n\n使用半角中括号包裹要查询的条目名，如 `[[帮助]]`\n\n使用半角大括号包裹要查询的模板名，如 `{{测试模板}}` \n\n（PS：直接使用`[[Template:模板名]]`也是可行的）\n\n此外，方便起见，也可以用`wiki 条目名` `wiki prefix:条目名`的方法查询\n\nBot会尝试去调取目标wiki的api,并获取对应标题的页面信息（默认允许重定向、跨wiki、简繁转换）。如果未找到对应条目，或者对应页面是消歧义页面，\n则会提供数字来选择。如果调用api失败或者未配置api，会回落到字符串拼接的方式生成链接。\n\n```plaintext\nTip：如果api返回的结果不是你想要的，可以使用半角小括号包裹条目名以绕过api，如 ((帮助))\n```\n\n当绑定了多个wiki时，需要指定前缀以查询默认wiki之外的wiki，例如，假如将某个wiki的前缀设置为flan，且不是默认wiki，则查询命令对应为[[flan:帮助]]\n\n### 管理功能\n\n* wiki列表\n  * 权限：所有人可用\n  * 语法：`wiki.list`\n  * 返回：当前群绑定的wiki列表，以及全局wiki列表\n\n#### 单个群的管理\n\n以下操作均需在目标群内进行，bot管理员和群管理员均有权限操作\n\n* 添加wiki\n  * 语法 `wiki.add`\n  * 参数：\n    * 前缀：用于区分wiki的前缀，仅支持字母、数字和下划线，不能和本群已有的重复，但可以和全局已有的重复，此时本地设置优先。另外，为了防止和mediawiki的名字空间冲突，bot默认屏蔽了部分名字空间名作为前缀的能力，也请在绑定前先了解目标wiki的名字空间情况。\n    * api地址（可选）：目标wiki的mediawiki api的地址。某些wiki可能限制api调用，此时可以回复`0`来不设置api。该地址通常可以在目标wiki的`Special:版本#接入点URL`页面中找到。或者也可以尝试这些一般的格式：\n    ```plaintext\n    https://www.example.org/api.php （如萌娘百科）\n    https://www.example.org/w/api.php (如维基百科）\n    ```\n    * 通用url：目标wiki的条目路径。通常来讲，在该url后加上正确的条目名即可访问目标条目。可以在目标wiki的`Special:版本#接入点URL`中找到（“条目路径”中的$1即条目名）\n    ```plaintext\n    例如，对维基百科：https://www.example.org/wiki\n    对萌百等：https://www.example.org/\n    ```\n\n\n* 删除wiki\n  * 语法 `wiki.delete`\n  * 参数：\n    * 前缀：要删除的wiki的前缀\n\n\n* 设置默认wiki\n  * 语法 `wiki.default`\n    * 参数：\n      * 前缀：要设置默认的wiki的前缀\n  ```plaintext\n  Tip：本群/全局绑定的的一个wiki将被自动设置为本地/全局的默认wiki,当本地/全局绑定的默认wiki被删除时会自动清除对应的默认wiki设置，无需手动操作。\n  ```\n\n\n#### 全局管理\n\n以下操作可以在群内进行，也可以私聊进行，只有bot管理员有权限操作\n\n* 添加全局wiki\n  * 语法：`wiki.add.global`\n    * 参数同上\n\n\n* 删除全局wiki\n  * 语法：`wiki.delete.global`\n    * 参数同上\n\n\n* 设置全局默认wiki\n  * 语法：`wiki.default.global`\n    * 参数同上\n\n### 附加说明\n#### 本地和全局\n\nbot管理员可以设置全局的wiki，全局wiki的设计意图在于回落，换句话说，本地设置无条件优先于全局设置。当且仅当在以下情况下，全局设置会被应用：\n\n1. 本地没有绑定任何wiki\n2. 本地没有设置默认前缀，而查询请求中又不包含前缀\n\n```plaintext\n注意：如果本地有和全局默认前缀相同的wiki时，本地的wiki仍将被优先调用\n```\n\n3. 本地设置了默认前缀，但是本地不存在该wiki\n\n```plaintext\n注意：当前缀在全局中也不存在时，前缀将被视为名字空间，直接和条目名一并传入api进行查询\n```\n\n4. 查询请求中包含的前缀在本地不存在\n\n#### API调用\n\n为了提供更准确的结果，默认情况下bot会调用mediawiki api查询条目。当api无法正常调用时，会使用通用url和条目名拼接作为回落。\n如果返回了错误的结果，可以使用小括号查询来绕过api。\n\n在某些情况下，你可能希望限制调用频率，如目标Wiki的api调用频率限制严格，或者目标wiki的防火墙会阻断高频请求 ~~（萌百：你报我域名算了）~~ 。\n为简化查询流程，本插件并不提供对应功能，~~(不然频率限制比核心功能代码还长了)~~ 。如果确有需求，可以考虑使用[Flandre](https://github.com/KoishiMoe/Flandre) ，她带有频率限制以及适配了频率限制的wiki组件。如果你将本插件独立使用，可以考虑使用其他频率限制插件来解决（不过nonebot目前似乎还没有这类插件……）。\n\n根据我个人在一些wiki项目的QQ群观摩 ~~（潜伏）~~  的经验来说，群bot的wiki功能被调用的频率并不会很高，因此除非你将bot同时置于多个群，\n并且都连接到同一个wiki,或者有人恶意利用bot（事实上由于bot不响应私聊的查询请求，要达到这种效果只能在群聊中刷屏），不然碰上调用频率限制的可能性还是很低的\n',
    'author': 'KoishiMoe',
    'author_email': '68314080+KoishiMoe@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/KoishiMoe/nonebot-plugin-mediawiki',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0.0',
}


setup(**setup_kwargs)
