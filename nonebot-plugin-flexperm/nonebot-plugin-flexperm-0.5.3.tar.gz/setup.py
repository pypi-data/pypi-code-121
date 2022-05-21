# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_flexperm']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.0.0b1,<3.0.0',
 'nonebot2>=2.0.0b1,<3.0.0',
 'ruamel.yaml>=0.17.10,<0.18.0']

setup_kwargs = {
    'name': 'nonebot-plugin-flexperm',
    'version': '0.5.3',
    'description': '精细化的 NoneBot 权限管理插件',
    'long_description': '# nonebot-plugin-flexperm\n\n精细化的 NoneBot 权限管理插件。\n\n提供对用户精确到人或群、对插件精确到指令或更细粒度的权限管理功能。\n\n## 安装\n\n- 使用 nb-cli\n\n```shell\nnb plugin install nonebot-plugin-flexperm\n```\n\n- 使用 poetry\n\n```shell\npoetry add nonebot-plugin-flexperm\n```\n\n- 使用 pip\n\n```shell\npip install nonebot-plugin-flexperm\n```\n\n## 依赖\n\n目前只支持 OneBot V11 协议，之后可能会支持其他协议。\n\n## 使用\n\n本插件主要通过 NoneBot 的 require 机制向**其他插件**提供功能。本插件也提供了一组命令，用于直接管理权限配置。\n\n```python\nfrom nonebot import require\nrequire("nonebot_plugin_flexperm")\nfrom nonebot_plugin_flexperm import register\nP = register("my_plugin")\n```\n\n`P`是一个可调用对象，以权限名为参数调用即可得到相应的检查器。`P`的其他接口详见[接口文档](docs/interface.md)。\n\n```python\nfrom nonebot import on_command\ncmd = on_command("my_command", permission=P("my_command"))\n\n@cmd.handle()\nasync def _(bot, event):\n    ...\n```\n\n这样，运行时只有具有`my_plugin.my_command`权限的用户或群才能使用该命令。\n\n### 权限配置文件\n\n权限配置文件使用 YAML 格式，详见[权限配置文档](docs/permdesc.md)。示例：\n\n```yaml\nanyone:\n  permissions:\n    - my_plugin.help\n\ngroup_admin:\n  permissions:\n    - my_plugin.my_command\n    - another_plugin.*\n    - -another_plugin.another_command\n```\n\n这个配置文件授予了所有用户`my_plugin.help`权限，同时授予了群管理员`my_plugin.my_command`权限和`another_plugin`下的所有子权限，但撤销`another_plugin.another_command`权限。\n\n### 命令\n\n权限配置文件可以在运行时修改，然后使用`/flexperm.reload`命令重新加载。\n\n也可以通过命令编辑权限配置，详见[命令文档](docs/command.md)。\n\n## 配置\n\n本插件使用两个配置项，均为可选。如需修改，写入 NoneBot 项目环境文件`.env.*`即可。\n\n- `flexperm_base`: 权限配置文件所在目录，默认为`permissions`。\n- `flexperm_debug_check`: 是否输出检查权限过程中的调试信息，默认为`false`。未启用 NoneBot 的调试模式时无效。\n\n## 鸣谢\n\n- [nonebot / nonebot2](https://github.com/nonebot/nonebot2)\n- [Mrs4s / go-cqhttp](https://github.com/Mrs4s/go-cqhttp)\n',
    'author': 'Muchan',
    'author_email': 'liuzh1773@buaa.edu.cn',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rmuchan/nonebot-plugin-flexperm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
