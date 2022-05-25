# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_wordcloud']

package_data = \
{'': ['*']}

install_requires = \
['emoji>=1.6.3,<2.0.0',
 'jieba>=0.42.1,<0.43.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-chatrecorder>=0.1.5,<0.2.0',
 'nonebot2[httpx]>=2.0.0-beta.2,<3.0.0',
 'tzdata',
 'wordcloud>=1.8.1,<2.0.0']

extras_require = \
{':python_version < "3.9"': ['backports.zoneinfo>=0.2.1,<0.3.0']}

setup_kwargs = {
    'name': 'nonebot-plugin-wordcloud',
    'version': '0.2.1',
    'description': '适用于 NoneBot2 的词云插件',
    'long_description': '<!-- markdownlint-disable MD033 MD036 MD041 -->\n\n<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# NoneBot Plugin WordCloud\n\n_✨ NoneBot 词云插件 ✨_\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/he0119/nonebot-plugin-wordcloud/main/LICENSE">\n    <img src="https://img.shields.io/github/license/he0119/nonebot-plugin-wordcloud.svg" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-wordcloud">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-wordcloud.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">\n  <a href="https://codecov.io/gh/he0119/nonebot-plugin-wordcloud">\n    <img src="https://codecov.io/gh/he0119/nonebot-plugin-wordcloud/branch/main/graph/badge.svg?token=e2ECtMI91C"/>\n  </a>\n</p>\n\n## 使用方式\n\n插件依赖 [nonebot-plugin-chatrecorder](https://github.com/MeetWq/nonebot-plugin-chatrecorder) 提供消息存储。\n\n待插件启动完成后，发送 `/今日词云`、`/昨日词云`、`/本周词云`、`/本月词云`、`/年度词云` 或 `/历史词云` 即可获取词云。\n\n如果想获取自己的词云，可在上述指令前添加 `我的`，如 `/我的今日词云`。\n\n## 配置项\n\n配置方式：直接在 `NoneBot` 全局配置文件中添加以下配置项即可。\n\n### wordcloud_width\n\n- 类型: `int`\n- 默认: `1920`\n- 说明: 生成图片的宽度\n\n### wordcloud_height\n\n- 类型: `int`\n- 默认: `1200`\n- 说明: 生成图片的高度\n\n### wordcloud_background_color\n\n- 类型: `str`\n- 默认: `black`\n- 说明: 生成图片的背景颜色\n\n### wordcloud_font_path\n\n- 类型: `str`\n- 默认: 自带的字体（思源黑体）\n- 说明: 生成图片的字体文件位置\n\n### wordcloud_stopwords_path\n\n- 类型: `str`\n- 默认: `None`\n- 说明: 结巴分词的 [停用词表](https://github.com/fxsjy/jieba#%E5%9F%BA%E4%BA%8E-tf-idf-%E7%AE%97%E6%B3%95%E7%9A%84%E5%85%B3%E9%94%AE%E8%AF%8D%E6%8A%BD%E5%8F%96) 位置\n\n### wordcloud_userdict_path\n\n- 类型: `str`\n- 默认: `None`\n- 说明: 结巴分词的 [自定义词典](https://github.com/fxsjy/jieba#%E8%BD%BD%E5%85%A5%E8%AF%8D%E5%85%B8) 位置\n\n### wordcloud_timezone\n\n- 类型: `str`\n- 默认: `None`\n- 说明: 用户自定义的 [时区](https://docs.python.org/zh-cn/3/library/zoneinfo.html)，留空则使用系统时区\n',
    'author': 'hemengyang',
    'author_email': 'hmy0119@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/he0119/nonebot-plugin-wordcloud',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
