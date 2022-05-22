# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pait',
 'pait.api_doc',
 'pait.api_doc.html',
 'pait.app',
 'pait.app.base',
 'pait.app.flask',
 'pait.app.flask.plugin',
 'pait.app.sanic',
 'pait.app.sanic.plugin',
 'pait.app.starlette',
 'pait.app.starlette.plugin',
 'pait.app.tornado',
 'pait.app.tornado.plugin',
 'pait.extra',
 'pait.model',
 'pait.plugin',
 'pait.util',
 'pait.util.grpc_inspect']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.7.3,<2.0.0', 'typing-extensions>=4.1.1,<5.0.0']

extras_require = \
{'redis': ['redis>=4.2.2,<5.0.0']}

setup_kwargs = {
    'name': 'pait',
    'version': '0.7.8',
    'description': 'Pait is a Python api tool. Pait enables your Python web framework to have type checking, parameter type conversion, interface document generation and can display your documents through Redoc or Swagger (power by inspect, pydantic)',
    'long_description': '![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1652600629491%E6%9C%AA%E5%91%BD%E5%90%8D.jpg)\n<p align="center">\n    <em>Python Api Tools, fast to code</em>\n</p>\n\n---\n**Documentation**: [https://so1n.me/pait/](https://so1n.me/pait/)\n\n**中文文档**: [https://so1n.me/pait-zh-doc/](https://so1n.me/pait-zh-doc/)\n\n---\n\n# pait\nPait is an api tool that can be used in any python web framework (currently only `flask`, `starlette`, `sanic`, `tornado` are supported, other frameworks will be supported once Pait is stable).\n\n> Note:\n>\n> mypy check 100%\n>\n> test coverage 95%+ (exclude api_doc)\n>\n> python version >= 3.7 (support postponed annotations)\n>\n> The following code does not specify, all default to use the `starlette` framework.\n\n# Feature\n - [x] Parameter checksum automatic conversion (parameter check depends on `Pydantic`)\n - [x] Parameter dependency verification\n - [x] Automatically generate openapi files\n - [x] Swagger, Redoc route\n - [x] gRPC Gateway route\n - [x] TestClient support, support response result verification\n - [x] Support for plugin extensions, such as the Mock plugin\n\n# Installation\n```Bash\npip install pait\n```\n# Simple Example\n```python\nfrom typing import Type\nimport uvicorn  # type: ignore\nfrom starlette.applications import Starlette\nfrom starlette.responses import JSONResponse\nfrom starlette.routing import Route\n\nfrom pait.app.starlette import pait, add_doc_route\nfrom pait.field import Body\nfrom pait.model.response import PaitResponseModel\nfrom pydantic import BaseModel, Field\n\n\nclass DemoResponseModel(PaitResponseModel):\n    class ResponseModel(BaseModel):\n        uid: int = Field()\n        user_name: str = Field()\n\n    description: str = "demo response"\n    response_data: Type[BaseModel] = ResponseModel\n\n\n@pait(response_model_list=[DemoResponseModel])\nasync def demo_post(\n    uid: int = Body.i(description="user id", gt=10, lt=1000),\n    user_name: str = Body.i(description="user name", min_length=2, max_length=4)\n) -> JSONResponse:\n    return JSONResponse({\'uid\': uid, \'user_name\': user_name})\n\n\napp = Starlette(routes=[Route(\'/api\', demo_post, methods=[\'POST\'])])\nadd_doc_route(app)\nuvicorn.run(app)\n```\n\n# How to used in other web framework?\nIf the web framework is not supported, which you are using.\n\nCan be modified sync web framework according to [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask.py)\n\nCan be modified async web framework according to [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette.py)\n# IDE Support\nWhile pydantic will work well with any IDE out of the box.\n- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)\n- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)\n\n# Full example\nFor more complete examples, please refer to [example](https://github.com/so1n/pait/tree/master/example)\n',
    'author': 'So1n',
    'author_email': 'so1n897046026@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/so1n/pait',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
