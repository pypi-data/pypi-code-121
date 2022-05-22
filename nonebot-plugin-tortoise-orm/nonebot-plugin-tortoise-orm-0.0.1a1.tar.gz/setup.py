# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_tortoise_orm']

package_data = \
{'': ['*']}

install_requires = \
['aiomysql>=0.1.1,<0.2.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'tortoise-orm[asyncpg]>=0.19.1,<0.20.0']

setup_kwargs = {
    'name': 'nonebot-plugin-tortoise-orm',
    'version': '0.0.1a1',
    'description': '一个通用数据库连接插件',
    'long_description': '# 通用 ORM 数据库连接插件\n\n> 施工中。。。\n\n- 参考 [example_bot](example_bot) 来创建一个 _聊天记录_ 插件吧~！\n\n## `.env` 设置\n\n参考配置：\n\n```ini\n# db_url=postgres://postgres@localhost:5432/postgres\ndb_url=sqlite://db.sqlite3\ndb_generate_schemas=false\n```\n\n### `db_url`\n\n#### 使用 `sqlite`\n\n直接使用相对路径来建立\n\n```ini\ndb_url=sqlite://db.sqlite3\n```\n\n如果时指定路径，则应该是\n\n```ini\ndb_url=sqlite:///data/db.sqlite\n```\n\n使用绝对路径 注意有三个 `/`\n\n#### 使用 `PostgreSQL`\n\n```ini\ndb_url=postgres://postgres:pass@db.host:5432/somedb\n```\n\n- 说明： `postgres://` 表示协议\n- `postgres:pass@` 表示登入账号和密码 如果没有密码则用 `postgres@`\n- `db.host:5432` 表示数据库的地址 和 端口 如果是本机 则为 `localhost:5432`\n- `/somedb` 表示数据库名\n\n#### 使用 `MySQL/MariaDB`\n\n```ini\ndb_url=mysql://myuser:mypass:pass@db.host:3306/somedb\n```\n\n跟上面的差不多\n\n### `db_generate_schemas`\n\n- 填入 `true` 或 `false`\n- 默认 `false`\n- 如为 `true` 则会在每次启动时，在空的数据库上初始化数据表\n  - 请在**第一次启动**或**有新数据表**时设置为 `true` 来初始化表，随后设置为`false` 关闭该功能\n\n## 数据库类型\n\n- [x] postgres\n- [x] sqlite\n- [x] MySQL/MariaDB\n\n其他待补充\n',
    'author': 'kexue',
    'author_email': 'x@kexue.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kexue-z/nonebot-plugin-tortoise-orm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
