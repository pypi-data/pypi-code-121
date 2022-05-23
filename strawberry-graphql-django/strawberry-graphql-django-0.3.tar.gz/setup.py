# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strawberry_django',
 'strawberry_django.auth',
 'strawberry_django.extensions',
 'strawberry_django.fields',
 'strawberry_django.mutations']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.0', 'strawberry-graphql>=0.109.0']

setup_kwargs = {
    'name': 'strawberry-graphql-django',
    'version': '0.3',
    'description': 'Strawberry GraphQL Django extension',
    'long_description': "# Strawberry GraphQL Django extension\n\n[![CI](https://github.com/la4de/strawberry-graphql-django/actions/workflows/main.yml/badge.svg)](https://github.com/la4de/strawberry-graphql-django/actions/workflows/main.yml)\n[![PyPI](https://img.shields.io/pypi/v/strawberry-graphql-django)](https://pypi.org/project/strawberry-graphql-django/)\n[![Downloads](https://pepy.tech/badge/strawberry-graphql-django)](https://pepy.tech/project/strawberry-graphql-django)\n\nThis package provides powerful tools to generate GraphQL types, queries, mutations and resolvers from Django models.\n\nInstalling `strawberry-graphql-django` package from the python package repository.\n\n```shell\npip install strawberry-graphql-django\n```\n\nFull documentation is available under [docs](https://github.com/strawberry-graphql/strawberry-graphql-django/tree/main/docs/index.md) github folder.\n\n## Supported features\n\n- GraphQL type generation from models\n- Filtering, pagination and ordering\n- Basic create, retrieve, update and delete (CRUD) types and mutations\n- Basic Django auth support, current user query, login and logout mutations\n- Django sync and async views\n- Unit test integration\n\n## Basic Usage\n\n```python\n# models.py\nfrom django.db import models\n\nclass Fruit(models.Model):\n    name = models.CharField(max_length=20)\n    color = models.ForeignKey('Color', blank=True, null=True,\n            related_name='fruits', on_delete=models.CASCADE)\n\nclass Color(models.Model):\n    name = models.CharField(max_length=20)\n```\n\n```python\n# types.py\nimport strawberry\nfrom strawberry import auto\nfrom typing import List\nfrom . import models\n\n@strawberry.django.type(models.Fruit)\nclass Fruit:\n    id: auto\n    name: auto\n    color: 'Color'\n\n@strawberry.django.type(models.Color)\nclass Color:\n    id: auto\n    name: auto\n    fruits: List[Fruit]\n```\n\n```python\n# schema.py\nimport strawberry\nfrom typing import List\nfrom .types import Fruit\n\n@strawberry.type\nclass Query:\n    fruits: List[Fruit] = strawberry.django.field()\n\nschema = strawberry.Schema(query=Query)\n```\n\nCode above generates following schema.\n\n```schema\ntype Fruit {\n  id: ID!\n  name: String!\n  color: Color\n}\n\ntype Color {\n  id: ID!\n  name: String!\n  fruits: [Fruit!]\n}\n\ntype Query {\n  fruits: [Fruit!]!\n}\n```\n\n```python\n# urls.py\nfrom django.urls import include, path\nfrom strawberry.django.views import AsyncGraphQLView\nfrom .schema import schema\n\nurlpatterns = [\n    path('graphql', AsyncGraphQLView.as_view(schema=schema)),\n]\n```\n\nSee complete Django project from github repository folder [examples/django](https://github.com/strawberry-graphql/strawberry-graphql-django/tree/main/examples/django).\n\n## Autocompletion with editors\n\nSome editors like VSCode may not be able to resolve symbols and types without explicit `strawberry.django` import. Adding following line to code fixes that problem.\n\n```python\nimport strawberry.django\n```\n\n## Running unit tests\n\n```shell\npoetry install\npoetry run pytest\n```\n\n## Pre commit hooks\n\nWe have a configuration for pre-commit, to add the hook run the following command:\n\n```shell\npre-commit install\n```\n\n## Contributing\n\nWe are happy to get pull requests and feedback from you.\n",
    'author': 'Lauri Hintsala',
    'author_email': 'lauri.hintsala@verkkopaja.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/strawberry-graphql/strawberry-graphql-django',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
