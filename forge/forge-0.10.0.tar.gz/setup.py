# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['forge',
 'forge.auth',
 'forge.cli',
 'forge.default_files',
 'forge.forms',
 'forge.management',
 'forge.management.commands',
 'forge.scaffold',
 'forge.scaffold.template.app',
 'forge.scaffold.template.app.teams',
 'forge.scaffold.template.app.teams.migrations',
 'forge.scaffold.template.app.tests',
 'forge.scaffold.template.app.users',
 'forge.scaffold.template.app.users.migrations',
 'forge.tailwind',
 'forge.views']

package_data = \
{'': ['*'],
 'forge': ['templates/*'],
 'forge.auth': ['templates/registration/*'],
 'forge.forms': ['templates/django/forms/*',
                 'templates/django/forms/errors/list/*'],
 'forge.scaffold': ['template/*',
                    'template/.github/workflows/*',
                    'template/scripts/*'],
 'forge.scaffold.template.app': ['static/src/*', 'templates/*'],
 'forge.scaffold.template.app.users': ['templates/registration/*',
                                       'templates/users/*']}

install_requires = \
['Django>=4.0,<5.0',
 'black>=22.1.0,<23.0.0',
 'click-didyoumean>=0.3.0,<0.4.0',
 'click>=8.1.0,<9.0.0',
 'dj-database-url>=0.5.0,<0.6.0',
 'django-widget-tweaks>=1.4.12,<2.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'hiredis>=2.0.0,<3.0.0',
 'honcho==1.1.0',
 'ipdb>=0.13.9,<0.14.0',
 'isort>=5.10.1,<6.0.0',
 'psycopg2-binary>=2.9.2,<3.0.0',
 'pytest-django>=4.5.2,<5.0.0',
 'pytest>=7.0.0,<8.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'redis>=4.2.2,<5.0.0',
 'requests>=2.0.0',
 'whitenoise>=6.0.0,<7.0.0']

entry_points = \
{'console_scripts': ['forge = forge.cli:cli']}

setup_kwargs = {
    'name': 'forge',
    'version': '0.10.0',
    'description': 'Quickly build a professional web app using Django.',
    'long_description': '# Forge\n\n**Quickly build a professional web app using Django.**\n\nForge is a set of opinions.\nIt guides how you work,\nchooses what tools you use,\nand makes decisions so you don\'t have to.\n\nAt it\'s core,\nForge *is* Django.\nBut we\'ve taken a number of steps to make it even easier to build and deploy a production-ready app on day one.\n\nIf you\'re an experienced Django user,\nyou\'ll understand and (hopefully) agree with some of Forge\'s opinions.\nIf you\'re new to Django or building web applications,\nwe\'ve simply removed questions that you might not even be aware of.\n\nForge will get you from *zero to one* on a revenue-generating SaaS, internal business application, or hobby project.\n\n## Quickstart\n\nStart a new project in 5 minutes:\n\n```sh\ncurl -sSL https://djangoforge.dev/quickstart.py | python3 - my-project\n```\n\n## What\'s included\n\nThings that come with Forge,\nthat you won\'t get from Django itself:\n\n- Configure settings with environment variables\n- A much simpler `settings.py`\n- Extraneous files (`manage.py`, `wsgi.py`, `asgi.py`) have been removed unless you need to customize them\n- Start with a custom user model (`users.User`)\n- Start with a "team" model (`teams.Team`)\n- Send emails using Django templates (ex. `templates/email/welcome.html`)\n- A starter `forge_base.html`\n- Default form rendering with Tailwind classes\n- Login in with email address (in addition to usernames)\n- Abstract models for common uses (UUIDs, created_at, updated_at, etc.)\n- Test using [pytest](https://docs.pytest.org/en/latest/) and [pytest-django](https://pytest-django.readthedocs.io/en/latest/)\n- Static files served with [WhiteNoise](http://whitenoise.evans.io/en/stable/)\n\nWe\'re also able to make some decisions about what tools you use *with* Django -- things that Django (rightfully) doesn\'t take a stance on:\n\n- Deploy using [Heroku](https://heroku.com/)\n- Manage Python dependencies using [Poetry](https://python-poetry.org/)\n- Style using [Tailwind CSS](https://tailwindcss.com/)\n- Format your code using [black](https://github.com/psf/black) and [isort](https://github.com/PyCQA/isort)\n\nLastly, we bring it all together with a `forge` CLI:\n\n### Local development\n\n- `forge work` - your local development command (runs `runserver`, Postgres, and Tailwind at the same time)\n- `forge test` - run tests using pytest\n- `forge format` - format app code with black and isort\n- `forge pre-commit` - checks tests and formatting before commits (installed as a git hook automatically)\n- `forge django` - passes commands to Django manage.py (i.e. `forge django makemigrations`)\n\n### Deployment\n\n- `forge pre-deploy` - runs Django system checks before deployment starts\n- `forge serve` - a production gunicorn process\n\n### Misc.\n\n- `forge init` - used by the quickstart to create a new project, but can be used by itself too\n\n## Inspired by\n\n- [create-react-app](https://create-react-app.dev/)\n- [Bullet Train](https://bullettrain.co/)\n- [SaaS Pegasus](https://www.saaspegasus.com/)\n- [Laravel Spark](https://spark.laravel.com/)\n',
    'author': 'Dave Gaeddert',
    'author_email': 'dave.gaeddert@dropseed.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.djangoforge.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
