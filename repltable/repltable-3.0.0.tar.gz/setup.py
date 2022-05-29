# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['repltable']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3.6.8,<4.0.0', 'urllib3>=1.26.9,<2.0.0']

setup_kwargs = {
    'name': 'repltable',
    'version': '3.0.0',
    'description': 'a better replit database for python',
    'long_description': '<center>\n    <h1>repltable</h1>\n    install](#⚙️-installation)\n</center>\n\n![PyPI - Downloads](https://img.shields.io/pypi/dm/repltable?style=for-the-badge)\n![code style](https://img.shields.io/badge/code%20style-black-black?style=for-the-badge&logo=python)\n\nthis is a project is to make it so that you can have tables in the replit db.\n\nthe main annoyance (for me) with replit is that it reverts a lot of database file changes, which forces you to use the repl.it database. also, you can\'t group together keys, and it takes *FOREVER* to install, due to it installing flask, aiohttp and a ton of other things you don\'t need for the database.\n\n## ⚙️ installation \n```bash\npip install repltable\n```\n\n## \U0001fab4 usage\n```python\n# if you are using this on replit\nfrom repltable import db\n\n# or...\nfrom repltable import Database\ndb = Database("https://kv.replit.com/v0/...")\n\n\n# repltable databases work like a dictionary\ndb.get(foo=\'bar\')\n>>> [{\'foo\': \'bar\'}]\n\n# repltable auto-creates tables if they don\'t exist\ndb.insert(dict(foo=\'bar\'))\n\n# you can get one, or get all matching documents\ndb.get_one(foo=\'bar\')\n>>> {\'foo\': \'bar\'}\n\n\n# you can also group keys together\nfrom repltable import TableDatabase\n\ntable = TableDatabase.get("users")\n# from here, it behaves as a regular database\n\ntable.get(foo=\'bar\')\n>>> [{\'foo\': \'bar\'}]\n\n# repltable auto-creates tables if they don\'t exist\ntable.insert(dict(foo=\'bar\'))\n\n# you can get one, or get all matching documents\ntable.get_one(foo=\'bar\')\n>>> {\'foo\': \'bar\'}\n```\n## ❓ why not just use replit-py?\nwell, my goal is to make it so that you can use repl.it databases without having to use replit-py. replit-py has **27** dependencies. repltable has **2**.\n\nplus, repltable has more features:\n- caching (auto-updates itself for accuracy!)\n- groups of keys (named tables)\n- uses more efficient queries (you can **filter** keys!)\n\n\n## 👥 contributing\nto contribute, fork the repo, make a branch, and send a pull request.\n\nfor local development, you can install the dependencies with poetry:\n```bash\npoetry install\n```\n\n## 📜 license\nthis project is licensed under the [mit](https://choosealicense.com/licenses/mit/) license.\n',
    'author': 'terabyte.',
    'author_email': 'terabyte@terabyteis.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/terabyte3/repltable',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
