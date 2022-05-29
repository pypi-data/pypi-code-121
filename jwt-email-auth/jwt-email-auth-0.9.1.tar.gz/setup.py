# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jwt_email_auth',
 'jwt_email_auth.rotation',
 'jwt_email_auth.rotation.migrations']

package_data = \
{'': ['*'], 'jwt_email_auth': ['locale/fi/LC_MESSAGES/*']}

install_requires = \
['Django>=3.2',
 'PyJWT>=2.3.0',
 'cffi>=1.15.0',
 'cryptography>=36.0.0',
 'django-ipware>=4.0.0',
 'django-settings-holder>=0.0.4',
 'djangorestframework>=3.12.0']

setup_kwargs = {
    'name': 'jwt-email-auth',
    'version': '0.9.1',
    'description': 'JWT authentication from email login codes.',
    'long_description': "# JSON Web Token Email Authentiation\n\n[![Coverage Status][coverage-badge]][coverage]\n[![GitHub Workflow Status][status-badge]][status]\n[![PyPI][pypi-badge]][pypi]\n[![GitHub][licence-badge]][licence]\n[![GitHub Last Commit][repo-badge]][repo]\n[![GitHub Issues][issues-badge]][issues]\n[![Python Version][version-badge]][pypi]\n\n```shell\npip install jwt-email-auth\n```\n\n---\n\n**Documentation**: [https://mrthearman.github.io/jwt-email-auth/](https://mrthearman.github.io/jwt-email-auth/)\n\n**Source Code**: [https://github.com/MrThearMan/jwt-email-auth/](https://github.com/MrThearMan/jwt-email-auth/)\n\n---\n\n\nThis module enables JSON Web Token Authentication in Django Rest framework without using Django's User model.\nInstead, login information is stored in [cache][cache], a login code is sent to the user's email inbox,\nand then the cached information is obtained using the code that was sent to the given email.\n\n\n[cache]: https://docs.djangoproject.com/en/3.2/topics/cache/#the-low-level-cache-api\n\n[coverage-badge]: https://coveralls.io/repos/github/MrThearMan/jwt-email-auth/badge.svg?branch=main\n[status-badge]: https://img.shields.io/github/workflow/status/MrThearMan/jwt-email-auth/Tests\n[pypi-badge]: https://img.shields.io/pypi/v/jwt-email-auth\n[licence-badge]: https://img.shields.io/github/license/MrThearMan/jwt-email-auth\n[repo-badge]: https://img.shields.io/github/last-commit/MrThearMan/jwt-email-auth\n[issues-badge]: https://img.shields.io/github/issues-raw/MrThearMan/jwt-email-auth\n[version-badge]: https://img.shields.io/pypi/pyversions/jwt-email-auth\n\n[coverage]: https://coveralls.io/github/MrThearMan/jwt-email-auth?branch=main\n[status]: https://github.com/MrThearMan/jwt-email-auth/actions/workflows/main.yml\n[pypi]: https://pypi.org/project/jwt-email-auth\n[licence]: https://github.com/MrThearMan/jwt-email-auth/blob/main/LICENSE\n[repo]: https://github.com/MrThearMan/jwt-email-auth/commits/main\n[issues]: https://github.com/MrThearMan/jwt-email-auth/issues\n",
    'author': 'Matti Lamppu',
    'author_email': 'lamppu.matti.akseli@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrThearMan/jwt-email-auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
