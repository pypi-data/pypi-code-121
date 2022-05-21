# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['annoworkapi']

package_data = \
{'': ['*']}

install_requires = \
['backoff', 'requests']

setup_kwargs = {
    'name': 'annoworkapi',
    'version': '3.0.1',
    'description': 'Python Clinet Library of AnnoWork WebAPI',
    'long_description': '# annowork-api-python-client\nAnnoWork WebAPIのPython用クライントライブラリです。\n\n[![Build Status](https://app.travis-ci.com/kurusugawa-computer/annowork-api-python-client.svg?branch=main)](https://app.travis-ci.com/kurusugawa-computer/annowork-api-python-client)\n[![PyPI version](https://badge.fury.io/py/annoworkapi.svg)](https://badge.fury.io/py/annoworkapi)\n[![Python Versions](https://img.shields.io/pypi/pyversions/annoworkapi.svg)](https://pypi.org/project/annoworkapi/)\n[![Documentation Status](https://readthedocs.org/projects/annowork-api-python-client/badge/?version=latest)](https://annowork-api-python-client.readthedocs.io/ja/latest/?badge=latest)\n\n\n\n# Requirements\n* Python 3.8+ \n\n# Install\n\n```\n$ pip install annoworkapi\n```\n\n# Usage\n\n## 認証情報の設定方法\n\n### `$HOME/.netrc`\n\n```\nmachine annowork.com\nlogin ${user_id}\npassword ${password}\n```\n\n### 環境変数に設定する場合\n環境変数`ANNOWORK_USER_ID`にユーザID, `ANNOWORK_PASSWORD` にパスワードを設定する。\n\n\n\n## 基本的な使い方\n\n```python\nimport annoworkapi\nservice = annoworkapi.build()\n\nresult = service.api.get_my_account()\nprint(result)\n# {\'account_id\': \'xxx\', ... }\n```\n\n\n## 応用的な使い方\n\n### ログの出力\n\n```python\nimport logging\nlogging_formatter = \'%(levelname)-8s : %(asctime)s : %(filename)s : %(name)s : %(funcName)s : %(message)s\'\nlogging.basicConfig(format=logging_formatter)\nlogging.getLogger("annoworkapi").setLevel(level=logging.DEBUG)\n```\n\n\n```\nIn [1]: c = s.api.get_actual_working_times_by_workspacen_member("a9956d30-b201-418a-a03b-b9b8b55b2e3d", "204bf4d9-4569-4b7b-89b9-84f089201247")\nDEBUG    : 2022-01-11 17:36:04,354 : api.py : annoworkapi.api : _request_wrapper : Sent a request :: {\'request\': {\'http_method\': \'get\', \'url\': \'https://annowork.com/api/v1/workspacens/a9956d30-b201-418a-a03b-b9b8b55b2e3d/members/204bf4d9-4569-4b7b-89b9-84f089201247/actual-working-times\', \'query_params\': None, \'header_params\': None, \'request_body\': None}, \'response\': {\'status_code\': 200, \'content_length\': 209988}}\n```\n\n\n# 開発者用ドキュメント\n[README_for_developer.md](https://github.com/kurusugawa-computer/annowork-api-python-client/blob/main/README_for_developer.md) 参照\n',
    'author': 'yuji38kwmt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kurusugawa-computer/annowork-api-python-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
