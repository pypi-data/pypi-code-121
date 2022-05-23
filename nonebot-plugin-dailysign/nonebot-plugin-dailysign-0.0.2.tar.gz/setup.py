# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_dailysign']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-tortoise-orm>=0.0.1-alpha.2,<0.0.2',
 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-dailysign',
    'version': '0.0.2',
    'description': '一个简单的每日签到插件',
    'long_description': '# 一个签到\n\n发送 `签到` 来签到\n\n有什么用？\n\n可以获取金币\n\n然后呢？\n\n就没了\n\n因为是写着玩练手的\n\n因为是用了刚刚摸鱼的 `nonebot_plugin_tortoise_orm` 来弄数据库啦\n\n[https://github.com/kexue-z/nonebot-plugin-tortoise-orm](https://github.com/kexue-z/nonebot-plugin-tortoise-orm)\n\n可以开发插件来获取金币？\n\n## 插件使用\n\n```python\n\nfrom nonebot_plugin_dailysign.models import DailySign\n\nawait DailySign.get_gold(user_id, group_id)\n# 获取金币\n\nawait DailySign.adjust_gold(adjust, user_id, group_id)\n# 更改金币数量 adjust 正负均可\n\n```\n\n## 计划\n\n- [ ] 用来减少 `SETU NOW` 插件的 CD\n',
    'author': 'kexue',
    'author_email': 'x@kexue.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kexue-z/nonebot-plugin-dailysign',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
