# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rouver', 'rouver_test']

package_data = \
{'': ['*']}

install_requires = \
['dectest>=1.0.0,<2.0.0', 'typing-extensions>=4.1.1,<5.0.0', 'werkzeug>=2.0,<3']

setup_kwargs = {
    'name': 'rouver',
    'version': '2.4.4',
    'description': 'A microframework',
    'long_description': '# Rouver\n\nA microframework for Python 3, based on werkzeug.\n\n[![MIT License](https://img.shields.io/pypi/l/rouver.svg)](https://pypi.python.org/pypi/rouver/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rouver)](https://pypi.python.org/pypi/rouver/)\n[![GitHub](https://img.shields.io/github/release/srittau/rouver/all.svg)](https://github.com/srittau/rouver/releases/)\n[![pypi](https://img.shields.io/pypi/v/rouver.svg)](https://pypi.python.org/pypi/rouver/)\n[![Travis CI](https://travis-ci.org/srittau/rouver.svg?branch=master)](https://travis-ci.org/srittau/rouver)\n\n## Routing\n\n```python\n>>> from rouver.router import Router\n>>> from rouver.response import respond_with_html, respond_with_json\n>>> def get_index(environ, start_response):\n...     return respond_with_html(start_response, "<div>Foo</div>")\n>>> def get_count(environ, start_response):\n...     return respond_with_json(start_response, {"count": 42})\n>>> router = Router()\n>>> router.add_routes([\n...     ("", "GET", get_index),\n...     ("count", "GET", get_count),\n... ])\n\n```\n\nRoutes with placeholders:\n\n```python\n>>> def get_addition(environ, start_response):\n...     num1, num2 = path\n...     return response_with_json(start_response, {"result": num1 + num2})\n>>> def numeric_arg(request, path, value):\n...     return int(value)\n>>> router.add_template_handler("numeric", numeric_arg)\n>>> router.add_routes([\n...     ("add/{numeric}/{numeric}", "GET", get_addition),\n... ])\n```\n\nRoutes with wildcards:\n\n```python\n>>> def get_wildcard(environ, start_response):\n...     # environ["rouver.wildcard_path"] contains the remaining path\n...     return respond(start_response)\n>>> router.add_routes([\n...     ("wild/*", "GET", get_wildcard),\n... ])\n```\n\nSub-routers:\n\n```python\n>>> def get_sub(environ, start_response):\n...     return respond(start_response)\n>>> sub_router = Router()\n>>> sub_router.add_routes([\n...     ("sub", "GET", get_sub),\n... ])\n>>> router.add_sub_router("parent", sub_router)\n```\n\n## Argument Handling\n\n```python\n>>> from rouver.args import Multiplicity, parse_args\n>>> from rouver.response import respond_with_json\n>>> def get_count_with_args(request, path, start_response):\n...     args = parse_args(request.environ, [\n...         ("count", int, Multiplicity.REQUIRED),\n...     ])\n...     return respond_with_json({"count": args["count"]})\n```\n\n## WSGI Testing\n\n```python\n>>> from rouver.test import create_request, test_wsgi_app\n>>> request = create_request("GET", "/my/path")\n>>> response = test_wsgi_app(app, request)\n>>> response.assert_status(HTTPStatus.OK)\n```\n',
    'author': 'Sebastian Rittau',
    'author_email': 'srittau@rittau.biz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/srittau/rouver',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
