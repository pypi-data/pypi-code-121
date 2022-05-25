# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['api_session']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'api-session',
    'version': '1.3.1',
    'description': 'requests.Session to work with (JSON) APIs',
    'long_description': '# api-session\n\n**api-session** is a small module providing an extended `requests.Session` class to work with (JSON) APIs.\n\nWe use it at [Bixoto](https://bixoto.com/) as a basis for JSON API clients such as [PyMagento][].\n\nIt aims at factoring the common parts of these clients while staying very lightweight (<100 SLOC).\n\n[PyMagento]: https://github.com/Bixoto/PyMagento\n\n## Features\n\n* base URL: the base API URL is given only once on object creation; subsequent calls use `.get("/path")`\n* read-only flag: if given, prevents the API from doing `POST` and similar calls\n* `requests.Session` inheritance: the class inherits from `requests.Session`, so it stays 100% compatible with it\n\n## Install\n\n    pip install api-session\n\nDependency: Python 3.8+.\n\n## Usage\n\n```python3\nfrom api_session import APISession\n\nclient = APISession("https://httpbin.org")\n\nclient.get_json_api("/get")\n# => {...}\n```\n',
    'author': 'Baptiste Fontaine',
    'author_email': 'baptiste@bixoto.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Bixoto/api-session',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
