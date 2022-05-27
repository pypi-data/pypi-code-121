# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tests', 'traderclient']

package_data = \
{'': ['*'], 'tests': ['data/*']}

install_requires = \
['arrow>=1.2.2,<2.0.0',
 'enum34>=1.1.10,<2.0.0',
 'fire>=0.4.0,<0.5.0',
 'httpx>=0.20,<0.21',
 'numpy>=1.22.4,<2.0.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['mkdocs>=1.2.3,<2.0.0',
         'mkdocs-include-markdown-plugin>=3.2.3,<4.0.0',
         'mkdocs-material>=8.1.11,<9.0.0',
         'mkdocstrings>=0.18.0,<0.19.0',
         'mkdocs-autorefs>=0.4.1,<0.5.0',
         'livereload>=2.6.3,<3.0.0'],
 'test': ['black>=22.3.0,<23.0.0',
          'isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest==6.1.2',
          'pytest-cov==2.10.1',
          'sanic>=22.3.2,<23.0.0']}

entry_points = \
{'console_scripts': ['bt = traderclient.cli:main']}

setup_kwargs = {
    'name': 'zillionare-trader-client',
    'version': '0.3.5',
    'description': 'Zillionare Trader Client',
    'long_description': '# 大富翁交易客户端\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/zillionare-trader-client">\n    <img src="https://img.shields.io/pypi/v/zillionare-trader-client.svg"\n        alt = "Release Status">\n</a>\n\n</p>\n\ntrade-client是大富翁量化框架中用来交易的客户端。它对回测和实盘提供了几乎相同的接口，从而使得经过回测的策略，可以无缝切换到实盘环境中。\n\n## 功能\n\n* 进行实盘和回测交易\n* 获取账号基本信息，比如本金、资产、持仓、盈亏及盈亏比等。\n* 交易函数，比如买入（限价和市价）、卖出（限价和市价）、撤单等\n* 查询委托、成交、持仓（当日和指定日期）\n* 查询一段时间内的账户评估指标，比如sharpe, sortino, calmar, voliality, win rate, max drawdown等。\n* 查询参照标的同期指标。\n\n## Credits\n\nThis package was created with [zillionare/python project wizard](https://zillionare.github.io/python-project-wizard) project template.\n',
    'author': 'Aaron Yang',
    'author_email': 'code@jieyu.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zillionare/trader-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
