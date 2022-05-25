# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chocs_middleware', 'chocs_middleware.trace']

package_data = \
{'': ['*']}

install_requires = \
['chocs>=1.5.3,<2.0.0', 'gid>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'chocs-middleware.trace',
    'version': '0.4.1',
    'description': 'Http tracing middleware for chocs library.',
    'long_description': '# Chocs-Trace <br> [![PyPI version](https://badge.fury.io/py/chocs-middleware.trace.svg)](https://pypi.org/project/chocs-middleware.trace/) [![CI](https://github.com/kodemore/chocs-trace/actions/workflows/main.yaml/badge.svg)](https://github.com/kodemore/chocs-trace/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/chocs-trace/actions/workflows/release.yml/badge.svg)](https://github.com/kodemore/chocs-trace/actions/workflows/release.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\nHttp tracing middleware for chocs library. \n\n\n# Installation\n\n### Poetry:\n```bash\npoetry add chocs-middleware.trace\n```\n\n### Pip:\n```bash\npip install chocs-middleware.trace\n```\n\n# Features\n\n- Automatic generation and propagation of tracing headers (x-request-id, x-correlation-id, x-causation-id)\n- Sentry integration\n- More intuitive log formatting options\n- Structured logging\n\n# Usage\n\n## Support tracing in your responses\n\n```python\nfrom chocs_middleware.trace import TraceMiddleware\nfrom chocs import Application, HttpRequest, HttpResponse\n\n# id_prefix will ensure generated tracing headers to contain your prefix\napp = Application(TraceMiddleware(id_prefix="service-name-"))\n\n\n@app.get("/hello")\ndef say_hello(req: HttpRequest) -> HttpResponse:\n    return HttpResponse("Hello!")  # tracing middleware will automatically attach x-request-id, x-correlation-id, x-causation-id headers to your response\n\n```\n\n## Tracing requests\n\n```python\nfrom chocs_middleware.trace import TraceMiddleware, HttpStrategy\nfrom chocs import Application, HttpRequest, HttpResponse\nimport requests\n\n# http_strategy will try to detect requests library and use it to add tracing headers in all your requests\n# if it fails to detect requests library it will fallback to urllib3\napp = Application(TraceMiddleware(http_strategy=HttpStrategy.AUTO))\n\n\n@app.get("/hello")\ndef say_hello(req: HttpRequest) -> HttpResponse:\n    \n    requests.get("http://example.com/test")  # middleware will automatically attach x-correlation-id, x-causation-id and x-request-id headers to your request\n    \n    return HttpResponse("Hello!")\n```\n\n## Using logger\n\n```python\nfrom chocs import Application, HttpRequest, HttpResponse\nfrom chocs_middleware.trace import TraceMiddleware, Logger\n\napp = Application(TraceMiddleware())\n\n\n@app.get("/hello")\ndef say_hello(req: HttpRequest) -> HttpResponse:\n    logger = Logger.get("logger_name")\n    logger.info("Hello {name}!", name="Bob")  # will output to log stream Hello Bob!\n    return HttpResponse("Hello!")\n```\n\n### Formatting message\n\n```python\nfrom chocs import Application, HttpRequest, HttpResponse\nfrom chocs_middleware.trace import TraceMiddleware, Logger\n\napp = Application(TraceMiddleware())\n\n\n@app.get("/hello")\ndef say_hello(req: HttpRequest) -> HttpResponse:\n    logger = Logger.get("logger_name", message_format="[{level}] {tags.request.x-correlation-id} {msg}")\n    logger.info("Hello {name}!", name="Bob")  # will output to log stream Hello Bob!\n    return HttpResponse("Hello!")\n```\n\n#### Available formatting options\n\n| Name | Example value | Description |\n|---|:---:|---|\n| `{level}` | DEBUG | Log level name |\n| `{msg}` | Example message | Log message after interpolation |\n| `{log_message}` | Example {name} | Log message before interpolation |\n| `{timestamp}` | 2022-03-07T20:06:23.453866 | Time of the logged message |\n| `{filename}` | example.py | Name of the python file where message was log |\n| `{funcName}` | example_function | Name of the function where message was log |\n| `{module}` | example_module | Name of the module where message was log |\n| `{pathname}` | example/path | Path name of the file where message was log |\n| `{tags.*}` | some value | Custom tag value set by calling `Logger.set_tag` function |\n\n\n',
    'author': 'Dawid Kraczkowski',
    'author_email': 'dawid.kraczkowski@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kodemore/chocs-trace',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
