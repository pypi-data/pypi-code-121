# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_view']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.0,<4.0.0', 'fastapi>=0.70.0', 'ujson>=5.0.0,<6.0.0']

setup_kwargs = {
    'name': 'fastapi-view',
    'version': '0.1.0',
    'description': 'A jinja2 view template helping function for FastAPI.',
    'long_description': '# fastapi-view\n\nA jinja2 view template helping function for FastAPI.\n\nFeatures:\n\n- Simply setting and use function to return Jinja2Templates\n\n## Installation\n\n```shell\npip install fastapi-view\n```\n\n# Usage\n\n- Configuring `fastapi-view` jinja2 templates directory path\n\n  ```python\n  from fastapi_view import view\n\n  # setting root view templates directory path\n  view.views_directory = "/your/jinja2/template/directory/path"\n  ```\n\n- Use view()\n\n  ```python\n  from fastapi import FastAPI\n  from fastapi.requests import Request\n  from fastapi_view.middleware import ViewRequestMiddleware\n  from fastapi_view import view\n\n  app = FastAPI()\n\n  from fastapi_view.middleware import ViewRequestMiddleware\n  app.add_middleware(ViewRequestMiddleware)\n\n  @app.get("/")\n  def index():\n      return view("index", {"foo": "bar"})\n\n  ```\n\n- Use inertia render\n\n  ```python\n  from fastapi import FastAPI\n  from fastapi.requests import Request\n  from fastapi_view.middleware import ViewRequestMiddleware\n  from fastapi_view import inertia\n\n  app = FastAPI()\n  app.add_middleware(ViewRequestMiddleware)\n\n  @app.get("/inertia/page")\n  def inertia_index():\n      return inertia.render("Index", props={"foo": "bar"})\n\n  ```\n',
    'author': 'Sam Yao',
    'author_email': 'turisesonia@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/turisesonia/fastapi-view.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
