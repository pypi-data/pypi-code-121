# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nwon_django_toolbox',
 'nwon_django_toolbox.admin',
 'nwon_django_toolbox.exception_handler',
 'nwon_django_toolbox.fields',
 'nwon_django_toolbox.fields.encrypted_text_field',
 'nwon_django_toolbox.fields.pydantic_json_field',
 'nwon_django_toolbox.files',
 'nwon_django_toolbox.fixtures',
 'nwon_django_toolbox.tests',
 'nwon_django_toolbox.tests.api',
 'nwon_django_toolbox.tests.api_helper',
 'nwon_django_toolbox.tests.celery',
 'nwon_django_toolbox.tests.helper',
 'nwon_django_toolbox.typings',
 'nwon_django_toolbox.typings.celery',
 'nwon_django_toolbox.url_helper',
 'nwon_django_toolbox.yasg']

package_data = \
{'': ['*']}

install_requires = \
['Pillow-PIL>=0.1dev,<0.2',
 'django-json-widget>=1.1.1,<2.0.0',
 'django-polymorphic>=3.1.0,<4.0.0',
 'django-rest-polymorphic>=0.1.9,<0.2.0',
 'django>=3.0',
 'drf-spectacular>=0.22.0,<0.23.0',
 'drf-yasg>=1.20.0,<2.0.0',
 'jsonref>=0.2,<0.3',
 'jsonschema-to-openapi>=0.2.1,<0.3.0',
 'nwon-baseline>=0.1.19,<0.2.0',
 'pydantic>=1.8.2',
 'pyhumps>=3.0.2,<4.0.0']

entry_points = \
{'console_scripts': ['prepare = scripts.prepare:prepare']}

setup_kwargs = {
    'name': 'nwon-django-toolbox',
    'version': '0.2.21',
    'description': 'Some Django Wizardry',
    'long_description': '# NWON-Django-Toolbox\n\nThis package provides some Django additions that can be used across several projects.\n\n## Settings\n\nThe Django Toolbox can be configured using the Django settings. We expect the key `NWON_DJANGO` that holds a dictionary. The dictionary must be of type `NWONDjangoSettings` that comes with this package (`nwon_django_toolbox.nwon_django_settings`). The keys mus be snake case or camel case.\n\nFor example like this\n\n```python\nNWON_DJANGO: NWONDjangoSettings = {\n    "authorization_prefix": "Bearer",\n    "logger_name": "your-log-name",\n    "application_name": "application"\n}\n```\n\n## Dependencies\n\nThe project has a bunch of dependencies that we use in most of our projects. In the end we have quite a lot and need to slim this down in the future.\n\nDjango related libraries are:\n\n- Django (Obviously 🧠)\n- django-polymorphic\n- django-json-widget\n- django-rest-polymorphic\n\nFor API documentation our models and serializer support two library which come as a dependency as well:\n\n- drf-spectacular\n- drf-yasg\n\nOn top we use a bunch of helper libraries\n\n- Pydantic\n- Pillow-PIL\n- jsonref\n- jsonschema-to-openapi\n- pyhumps\n- nwon-baseline\n\nPackage is meant for internal use at [NWON](https://nwon.de) as breaking changes may occur on version changes. This may change at some point but not for now 😇.\n\n## Development Setup\n\nWe recommend developing using poetry.\n\nThis are the steps to setup the project with a local virtual environment:\n\n1. Tell poetry to create dependencies in a `.venv` folder withing the project: `poetry config virtualenvs.in-project true`\n1. Create a virtual environment using the local python version: `poetry env use $(cat .python-version)`\n1. Install dependencies: `poetry install`\n\n## Prepare Package\n\nBefore publishing the package we need to:\n\n1. Clean dist folder\n1. Bump up the version of the package\n1. Build the package\n\nLuckily we provide a script for doing all of this `python scripts/prepare.py patch`. Alternatively you can run the script in a poetry context `poetry run prepare patch`. The argument at the end defines whether you want a `patch`, `minor` or `major` version bump.\n\nThe final zipped data ends up in the `dist` folder.\n\n## Publish Package \n\nTest package publication\n\n1. Add test PyPi repository: `poetry config repositories.testpypi https://test.pypi.org/legacy/`\n2. Publish the package to the test repository: `poetry publish -r testpypi`\n3. Test package: `pip install --index-url https://test.pypi.org/simple/ nwon_baseline`\n\nIf everything works fine publish the package via `poetry publish`.\n',
    'author': 'Reik Stiebeling',
    'author_email': 'reik.stiebeling@nwon.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://nwon.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
