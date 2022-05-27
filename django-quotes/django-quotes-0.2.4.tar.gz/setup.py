# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_quotes',
 'django_quotes.api',
 'django_quotes.management',
 'django_quotes.management.commands',
 'django_quotes.migrations']

package_data = \
{'': ['*'], 'django_quotes': ['static/*', 'templates/*', 'templates/quotes/*']}

install_requires = \
['Django>=4.0.2,<5.0.0',
 'Markdown>=3.3.6,<4.0.0',
 'django-cors-headers>=3.11.0,<4.0.0',
 'django-crispy-forms>=1.14.0,<2.0.0',
 'django-model-utils>=4.2.0,<5.0.0',
 'djangorestframework>=3.13.1,<4.0.0',
 'docutils>=0.18.1,<0.19.0',
 'drf-spectacular>=0.21.2,<0.23.0',
 'loguru>=0.6.0,<0.7.0',
 'markovify>=0.9.3,<0.10.0',
 'python-slugify>=6.1.1,<7.0.0',
 'rules>=3.1,<4.0',
 'spacy>=3.2.2,<4.0.0']

setup_kwargs = {
    'name': 'django-quotes',
    'version': '0.2.4',
    'description': 'A reusable Django app to collect quotes for use in random retrieval or generation of sentences using Markov Chains.',
    'long_description': '# Django Quotes\n\nA simple reusable [Django](https://www.djangoproject.com) app that allows you to collect quotes from arbitrary groups of characters, and then serve random quotes or Markov-chain generated sentences based upon them. Includes a Bootstrap compatible set of templates an optional REST API.\n\n![PyPI](https://img.shields.io/pypi/v/django-quotes)\n[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/andrlik/django-quotes/blob/main/.pre-commit-config.yaml)\n[![License](https://img.shields.io/github/license/andrlik/django-quotes)](https://github.com/andrlik/django-quotes/blob/main/LICENSE)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/andrlik/django-quotes/releases)\n![Test results](https://github.com/andrlik/django-quotes/actions/workflows/ci.yml/badge.svg)\n![Codestyle check results](https://github.com/andrlik/django-quotes/actions/workflows/codestyle.yml/badge.svg)\n[![Coverage Status](https://coveralls.io/repos/github/andrlik/django-quotes/badge.svg?branch=main)](https://coveralls.io/github/andrlik/django-quotes?branch=main)\n[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://andrlik.github.io/django-quotes/)\n\n## Features\n\n- Documentation and a full test suite.\n- Support for abstract grouping of quote sources.\n- Convenience methods for fetching a random quote.\n- Object-level permissions via [django-rules](https://github.com/dfunckt/django-rules).\n- Generate sentences based off of a Markov-chain for individual sources and groups using natural language processing.\n- Bootstrap-compatible templates.\n- A simple REST API for fetching data via JSON with CORS support.\n\nCheck out [the documentation](https://andrlik.github.io/django-quotes/) for installation and quickstart instructions.\n',
    'author': 'Daniel Andrlik',
    'author_email': 'daniel@andrlik.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrlik/django-quotes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
