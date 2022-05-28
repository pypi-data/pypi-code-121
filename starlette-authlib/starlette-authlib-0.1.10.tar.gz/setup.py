# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starlette_authlib']

package_data = \
{'': ['*']}

install_requires = \
['authlib<1.1', 'starlette<0.21', 'uvicorn<0.18']

setup_kwargs = {
    'name': 'starlette-authlib',
    'version': '0.1.10',
    'description': "A drop-in replacement for Starlette session middleware, using authlib's jwt",
    'long_description': "# Starlette Authlib Middleware\n\n[![Build Status](https://travis-ci.org/aogier/starlette-authlib.svg?branch=master)](https://travis-ci.org/aogier/starlette-authlib)\n[![codecov](https://codecov.io/gh/aogier/starlette-authlib/branch/master/graph/badge.svg)](https://codecov.io/gh/aogier/starlette-authlib)\n[![Package version](https://badge.fury.io/py/starlette-authlib.svg)](https://pypi.org/project/starlette-authlib)\n[![Total alerts](https://img.shields.io/lgtm/alerts/g/aogier/starlette-authlib.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/aogier/starlette-authlib/alerts/)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/aogier/starlette-authlib.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/aogier/starlette-authlib/context:python)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/starlette-authlib)\n\n## Introduction\n\nA drop-in replacement for Starlette session middleware, using [authlib's jwt](https://docs.authlib.org/en/latest/jose/jwt.html)\n\n## Requirements\n\n* Python 3.7+\n* Starlette 0.9+\n\n## Installation\n\n```console\npip install starlette-authlib\n```\n\n## Usage\n\nA complete example where we drop-in replace standard session middleware:\n\n```python\nfrom starlette.applications import Starlette\n\nfrom starlette_authlib.middleware import AuthlibMiddleware as SessionMiddleware\n\n\napp = Starlette()\n\napp.add_middleware(SessionMiddleware, secret='secret')\n```\n\nOther things you can configure either via environment variables or `.env` file:\n\n* `DOMAIN` - declare cookie domain. App must be under this domain. If empty,\n  the cookie is restricted to the subdomain of the app (this is useful when you\n  write eg. SSO portals)\n* `JWT_ALG` - one of authlib JWT [supported algorithms](https://docs.authlib.org/en/latest/specs/rfc7518.html#specs-rfc7518)\n* `JWT_SECRET` - jwt secret. Only useful for HS* algorithms, see the\n  `sample_app` folder for middleware usage w/ crypto keys.\n\n## Contributing\n\nThis project is absolutely open to contributions so if you have a nice idea,\ncreate an issue to let the community discuss it.\n",
    'author': 'Alessandro Ogier',
    'author_email': 'alessandro.ogier@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aogier/starlette-authlib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
