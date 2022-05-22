# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modernrpc', 'modernrpc.auth', 'modernrpc.conf', 'modernrpc.handlers']

package_data = \
{'': ['*'],
 'modernrpc': ['templates/modernrpc/bootstrap4/*',
               'templates/modernrpc/default/*']}

install_requires = \
['django>=2.1']

extras_require = \
{'docutils': ['docutils'], 'markdown': ['markdown']}

setup_kwargs = {
    'name': 'django-modern-rpc',
    'version': '1.0.0a2',
    'description': 'Simple and powerful RPC server for your Django project',
    'long_description': '# django-modern-rpc\n\n[![Downloads](https://pepy.tech/badge/django-modern-rpc)](https://pepy.tech/project/django-modern-rpc)\n[![Tests](https://github.com/alorence/django-modern-rpc/actions/workflows/default.yml/badge.svg)](https://github.com/alorence/django-modern-rpc/actions/workflows/default.yml)\n[![Documentation Status](https://readthedocs.org/projects/django-modern-rpc/badge/?version=main)](https://django-modern-rpc.readthedocs.io/en/latest/?badge=main)\n[![Link to demo](https://img.shields.io/badge/demo-online-blue.svg)](http://modernrpc.herokuapp.com/)\n\nBuild an XML-RPC and/or JSON-RPC server as part of your Django project. Major Django and Python versions are supported\n\n## Main features\n\n- XML-RPC and JSON-RPC 2.0 support (JSON-RPC 1.0 is NOT supported)\n- HTTP Basic Auth & custom authentication methods\n- Multiple entry-points: group your RPC methods under different paths to apply specific rules, authentication,\nprotocol support, etc.\n- API docs generation (based on docstring)\n\n## Requirements\n\nThe following Django / Python version are supported, according to Django requirements (see\n[here](https://docs.djangoproject.com/fr/2.2/faq/install/#faq-python-version-support) and\n[here](https://docs.djangoproject.com/fr/3.2/faq/install/#faq-python-version-support))\n\n| 🠗 Django \\ Python 🠖 | 3.5 | 3.6 | 3.7 | 3.8 | 3.9 | 3.10 |\n|-----------------------|:---:|:---:|:---:|:---:|:---:|:----:|\n| 2.1                   | 🟩  | 🟩  | 🟩  | 🟥  | 🟥  |  🟥  |\n| 2.2                   | 🟩  | 🟩  | 🟩  | 🟩  | 🟩  |  🟥  |\n| 3.0                   | 🟥  | 🟩  | 🟩  | 🟩  | 🟩  |  🟥  |\n| 3.1                   | 🟥  | 🟩  | 🟩  | 🟩  | 🟩  |  🟥  |\n| 3.2                   | 🟥  | 🟩  | 🟩  | 🟩  | 🟩  |  🟩  |\n| 4.0                   | 🟥  | 🟥  | 🟥  | 🟩  | 🟩  |  🟩  |\n\n## Setup\n\nA quick start is available as part of the documentation to help setting up you project:\nhttps://django-modern-rpc.readthedocs.io/en/latest/quickstart.html\n\n## Code quality\n\nContinuous integration and code analysis is performed automatically to ensure a decent code quality. Project health\nis publicly available on following apps:\n\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/37607e2ecaf549b890fc6defca88c7f8)](https://www.codacy.com/gh/alorence/django-modern-rpc/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alorence/django-modern-rpc&amp;utm_campaign=Badge_Grade)\n[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/37607e2ecaf549b890fc6defca88c7f8)](https://www.codacy.com/gh/alorence/django-modern-rpc/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alorence/django-modern-rpc&utm_campaign=Badge_Coverage)\n[![Coverage Status](https://coveralls.io/repos/github/alorence/django-modern-rpc/badge.svg)](https://coveralls.io/github/alorence/django-modern-rpc)\n',
    'author': 'Antoine Lorence',
    'author_email': 'antoine.lorence@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alorence/django-modern-rpc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
