# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tdf_tools',
 'tdf_tools.pipelines',
 'tdf_tools.tools',
 'tdf_tools.tools.cli',
 'tdf_tools.tools.config',
 'tdf_tools.tools.gitlab',
 'tdf_tools.tools.module',
 'tdf_tools.tools.package',
 'tdf_tools.tools.translate',
 'tdf_tools.tools.vscode']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.4.0,<0.5.0',
 'googletrans==3.1.0a0',
 'python-gitlab==1.15.0',
 'requests==2.27.1',
 'ruamel.yaml>=0.17.21,<0.18.0']

entry_points = \
{'console_scripts': ['tdf_tools = tdf_tools.app:main']}

setup_kwargs = {
    'name': 'tdf-tools',
    'version': '2.0.14',
    'description': '二维火 flutter 脚手架工具',
    'long_description': '## 帮助文档\n\n```shell\nNAME\n    tdf_tools - 二维火 Flutter 脚手架工具，包含项目构建，依赖分析，git等功能。。\n\nSYNOPSIS\n    tdf_tools GROUP | COMMAND\n\nDESCRIPTION\n    二维火 Flutter 脚手架工具，包含项目构建，依赖分析，git等功能。。\n\nGROUPS\n    GROUP is one of the following:\n\n     module\n       模块相关工具： tdf_tools module -h 查看详情\n\n     package\n       封包工具相关：tdf_tools package -h 查看详情\n\n     translate\n       国际化相关：tdf_tools translate -h 查看详情\n\nCOMMANDS\n    COMMAND is one of the following:\n\n     git\n       tdf_tools git【git 命令】：批量操作 git 命令, 例如 tdf_tools git push\n\n     router\n       tdf_tools router：会以交互式进行路由操作，对指定的模块执行路由生成和路由注册逻辑\n\n     upgrade\n       tdf_tools upgrade：升级插件到最新版本\n        \n```\n\n\n\n## 插件安装方式\n\n安装python包\n\n```\npip3 install tdf-tools --user\n```\n\n安装并更新python包\n\n```\npip3 install --upgrade tdf-tools --user\n```\n\n安装测试环境python包\n\n```\npip3 install -i https://test.pypi.org/simple/ tdf-tools --user\n```\n\n安装并更新测试环境python包\n\n```\npip3 install --upgrade -i https://test.pypi.org/simple/ tdf-tools --user\n```\n\n\n\n## 工具使用流程说明\n\n### 1.准备工作\n\n- 确保python的bin插件目录已经被配置到环境变量中（这一步不满足的话，插件安装之后是无法识别到本插件命令的）\n\n- 在~目录下，创建.tdf_tools_config文件并配置相关必需属性如下\n\n```json\ngit_private_token=***\n```\n\ngit_private_token是gitlab的token\n\n获取途径：进入gitlab页面，点击右上角头像，选择Preferences，选择左侧列表中的AccessToken进行创建\n\n**上述步骤如果没有做，会在使用插件时，会有提示**\n\n### 2.初始化\n\n#### i.进入壳目录（确保执行命令在壳目录内）\n\n#### ii.执行tdf_tools module init\n\n- 判断当前目录是否存在tdf_cache，若不存在，则会自动创建tdf_cache\n- 自动读取当前壳模块名称，写入initial_config.json配置文件；\n- 读取当前壳分支，写入initial_config.json配置文件；\n- 交互式提示用户输入需要开发的模块名并写入initial_config.json配置文件的moduleNameList列表字段中\n- ！退出，即输入完成\n- 自动clone所有开发模块到  ```../.tdf_flutter```  隐藏目录中；\n- 将所有开发模块分支切换至与壳一致；\n- 自动分析依赖树，并**由下至上**对所有模块自动执行```flutter pub upgrade```;\n\n#### iii.开发过程中\n\n##### 1.开发模块添加\n\n- 若是有新模块需要添加入开发模块中，可直接修改initial_config.json配置文件，修改moduleNameList字段；\n- 执行tdf_tools deps更新依赖\n\n##### 2.新开发模块添加\n\n- 添加新模块后，会提示找不到模块，实际查找的是```tdf_cache```文件夹中的module_config.json文件；\n- 如果没有找到该模块，则可以执行```tdf_tools module-update```,更新远程module_config.json文件；\n- 删掉本地的module_config.json文件，重新执行命令即可，脚本会自动判断本地是否存在该配置文件，如果不存在会**下载**；\n\n<span style="color:#ff0000">请确保gitlab仓库的新开发模块master分支是一个flutter模块，如果判定不是flutter模块，则会报错（判定条件为存在pubspec.yaml文件）</span>\n\n\n\n### 3.版本控制\n\n版本控制请使用tdf_tools命令，命令详情可使用  ```tdf_tools -h```  查看，现已支持大部分命令，若有特殊命令需要执行，可以使用  ```tdf_tools <git命令>``` ，如：```tdf_tools git add .```\n\n\n\n### 4.自动打包发布\n\n暂未接入打包工具，预计下一季度进行支持；\n\n\n\n**<span style="color:#ff0000">FAQ</span>**\n\nwindows系统请使用bash命令；\n\n\n\n## 额外功能说明\n\n### 1.二维数组表达依赖树\n\n生成一个二维数组，可根据该二维数组的数据进行**并发**打tag，每一层的模块，都可以同时进行打tag发布操作，减少发布耗时；\n\n```json\n[\n\t["tdf_channel", "tdf_event", "tdf_network"], \n\t["tdf_widgets"], \n\t["tdf_smart_devices", "tdf_account_module"], \n\t["flutter_reset_module"]\n]\n```\n\n如上数据，数组中每一个节点中的模块均可同时打tag，节点之间需要由上至下的顺序进行tag操作\n\n\n\n### 2.插件更新\n\n执行 ```tdf_tools upgrade```\n\n\n\n### 3.远程模块配置文件更新\n\n执行 ```tdf_tools module module_update```\n\n\n\n## 依赖树分析原理\n\n采用有向有/无环图进行依赖树的分析\n\n数据结构采用如下：\n\n```python\nclass DependencyNode:\n    def __init__(self):\n        self.nodeName = \'\'\n        self.parent = []  # 父亲节点列表\n        self.children = []  # 子孙节点列表\n        self.delete = False\n```\n\n![dependency](./README_DIR/dependency.png)\n\n如上图1：一个正常的依赖树表示；\n\n如上图2：对图1中，依赖树所有节点去重，变换为图2有向图；\t\n\n\n\n**分析流程：**\n\n**依赖图构建**\n\n```python\n# 生成依赖图\n    def _generateDependenciesMap(self):\n        for package in self.__moduleDependenciesMap:\n            for module in moduleNameList:\n                if package == module:\n                    # 到这一步表明当前这个模块属于开发模块且在当前模块的依赖模块列表中，是当前模块的子模块\n                    self._mNodeDict[self.__moduleName].children.append(package)\n                    self._mNodeDict[package].parent.append(self.__moduleName)\n```\n\n- 共5个节点\n\n  - node构建：\n\n    - ```python\n      {\n      \t"模块1":{\n          "nodeNmae": "模块1",\n          "parent": [],\n          "children": ["模块2","模块3","模块4","模块5"],\n          "delete": False\n      \t},\n      \t"模块2":{\n          "nodeNmae": "模块2",\n          "parent": ["模块1"],\n          "children": ["模块4","模块5"],\n          "delete": False\n      \t}\n      \t"模块3":{\n          "nodeNmae": "模块3",\n          "parent": ["模块1"],\n          "children": ["模块5"],\n          "delete": False\n      \t}\n      \t"模块4":{\n          "nodeNmae": "模块4",\n          "parent": ["模块1","模块2"],\n          "children": [],\n          "delete": False\n      \t}\n      \t"模块5":{\n          "nodeNmae": "模块5",\n          "parent": ["模块1","模块2","模块3"],\n          "children": [],\n          "delete": False\n      \t}\n      }\n      ```\n\n**依赖图解析伪代码（以一维数组为例）**\n\n```python\n# 返回二维数组，用于并发打tag\n    def _generateDependenciesOrder(self):\n        resList = []\n        while 存在节点delete属性不为True:\n            \n            for：查找子节点为0的节点\n            \t设置节点delete属性为True\n              \n            for：deleteItemList = 拿到所有delete属性为true的节点\n\n            for：遍历所有节点，如果节点的子节点中包含deleteItemList的节点，则将其从子节点列表中删除\n```\n\n\n\n\n\n- **initial_config.json文件说明**\n\n  ```json\n  {\n      "featureBranch": "feature/test_dev_1", // 开发分支\n      "shellName": "flutter_reset_module",\n      // 项目需要开发的模块,可自由配置\n      "moduleNameList": [\n          "flutter_reset_module",\n          "tdf_smart_devices",\n          "tdf_widgets",\n          "tdf_channel"\n      ]\n  }\n  ```\n\n- **module_config.json文件说明**\n\n  ```json\n  {\n      "flutter_globalyun_us_module": {\n        \t"id": "11111"\n          "type": "shell",\n          "git": "git@git.2dfire.net:app/flutter/app/flutter_globalyun_us_module.git"\n      },\n      "tdf_router_anno": {\n          "type": "base",\n          "git": "git@git.2dfire.net:app/flutter/app/tdf_router_anno.git"\n      },\n  }\n  //语意\n  {\n    "模块名":{\n      "id": 项目gitlab id\n      "类型": gitlab group名\n      "git": gitlab地址\n    }\n  }\n  ```\n\n\n\n## 后续计划\n\n<span style="color:#ff0000">**问题：**</span>由于现在flutter ci 【lint】【tag】任务脚本成功率过于低，很多时候是因为项目模块的配置问题导致的，且后续会接入一键打tag工具\n\n方案：在执行统一push前，对所有模块的项目配置信息进行校验，确保数据规范；\n\n\n\n## 插件打包发布命令\n\n**插件打包命令**\n\n```\npoetry build\n```\n**插件发布命令**\n\n```\npoetry publish\n```\n\n## History\n\n### 2.0.01\n\n- Cli 框架升级；\n- 代码重构；\n\n### **1.1.00（2022-4-28）**\n\n- 国际化解决输出json中包含转义字符的问题，如\\n；\n- 四类语言输出文件自动格式化\n\n### **1.0.55（2022-4-28）**\n\n- 国际化key使用中文（依照ios项目开发形式）；\n\n### **1.0.53（2022-4-28）**\n\n- 国际化流程中，兼容解决部分json解析失败问题，譬如字符串中包含"="符号；\n\n> 错误日志如：Unterminated string starting at: line 1 column 5650 (char 5649)\n\n### **1.0.50（2022-4-28）**\n\n- 国际化增加繁体字翻译；\n\n',
    'author': 'Jian Xu',
    'author_email': '17826875951@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.2dfire.net/app/flutter/tools/package_tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.9,<4.0.0',
}


setup(**setup_kwargs)
