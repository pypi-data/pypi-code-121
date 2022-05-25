# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_spinproject', 'django_spinproject.bin']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['django-spinproject = '
                     'django_spinproject.bin.spinproject:main']}

setup_kwargs = {
    'name': 'django-spinproject',
    'version': '1.4.0',
    'description': 'Opinionated version of `startproject` with some popular third-party packages. Starter pack includes: whitenoise, django-environ, logging, GitHub Scripts to Rule Them All, basic Dockerfile and Makefile.',
    'long_description': "# django-spinproject\n\nOpinionated version of `django-admin startproject` that intends to go further and do things that startproject can't do but most people will do anyway. Here's what you get:\n\n* ⚛️ **Whitenoise**: usually you don't need that during local development but one day you're going to deploy your project and find out that it ignores the `static/` folder when running under gunicorn — which is sorta fine because big applications usually serve static files separately via nginx. Smaller apps with small number of assets, however, usually serve them within the same process, which is what whitenoise is for.\n* 🔧 **settings.py**: it's slightly modified to also understand environment variables and `.env` files. This functionality requires the `django-environ` package. Also, app logger is mostly pre-configured for you.\n* 🔒 **Support for marking PostgreSQL databases as read-only**.\n* 🧰 `script/bootstrap` and other [scripts to rule them all](https://github.blog/2015-06-30-scripts-to-rule-them-all/) so your fellow developers and maintainers don't ask you how to run this thing. Current versions of these scripts optimized for use with [poetry](https://python-poetry.org/), but you can easily adapt them for any Python package manager.\n* 🏗️ **Dockerfile and .dockerignore**: one day your app will go to production, and we've got you covered.\n* 🏛️ **Gitlab CI config**: CI is a good thing.\n* ⚕️ **Pre-configured linter** so you can find some common problems automagically.\n* 🏃 **Pre-configured pytest** because you are going to need unit tests one day.\n* *️⃣ **.gitignore**: well, you know why.\n\n## Requirements\n\n* \\*nix system;\n* `django-admin` installed and available from `$PATH`.\n\nGenerated files will work fine in Django >= 2.0, not tested in earlier versions.\n\n## How to use\n\n1. Install the package: `pip install django-spinproject`\n2. `django-spinproject <path>`\n\n## Planned features\n\n(for requests, create an issue or drop me a line at m1kc@yandex.ru)\n\n* Some CLI flags to switch off the things you don't need.\n\n## Changelog\n\n### v1.3.0: Regular release\n\n* `74d6ff5` Fix Docker build failing because of new Debian release. Closes #12.\n* `ce0255f` Set `CI=true` when running `cibuild`. Closes #15.\n* `3d54ece` Dockerfile: run `migrate` on boot\n* `f9700fd` Allow script/setup to create .env file. Closes #13.\n* `13230bb` Add ruby-foreman to Docker image\n* `180a360` Remove gunicorn options from Dockerfile. Closes #16.\n* `d2bf875` Warn about psycopg2 dependency. Closes #10.\n* `0d05f5e` Ignore *~ files. Closes #11.\n* `3933d52` Use script/setup in CI. Closes #17.\n\n### Jun 21, 2021\n\n* pytest support 'cause you don't want to waste time on setting that up (give it a try: `script/test`);\n* Always call the settings directory `main` 'cause that's the only way to keep people sane when switching projects;\n* Add GitLab CI config generator 'cause you don't want to write one yourself;\n* flake8 isn't expected to be installed on your host system anymore.\n\n### Apr 16, 2021\n\n* `.gitignore` to keep your VCS clean;\n* `.dockerignore` to keep your Docker images clean;\n* `make clean` to get rid of `__pycache__` files when you need that;\n* No need to install `django-postgres-readonly` anymore.\n\n### Feb 5, 2021\n\n* To avoid confusion, `python3` executable is now used instead of `python`.\n\n### Feb 20, 2020\n\n* Makefile now includes an additional target, `lint`, for linting your project with `flake8`. Give it a try: `$ make lint`.\n* Dockerfile now works properly with most recent version of Poetry.\n",
    'author': 'm1kc (Max Musatov)',
    'author_email': 'm1kc@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/m1kc/django-spinproject',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
