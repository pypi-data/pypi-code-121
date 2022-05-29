# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['settings_holder']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'django-settings-holder',
    'version': '0.0.4',
    'description': 'Object that allows settings to be accessed with attributes.',
    'long_description': '# Django Settings Holder\n\n[![Coverage Status][coverage-badge]][coverage]\n[![GitHub Workflow Status][status-badge]][status]\n[![PyPI][pypi-badge]][pypi]\n[![GitHub][licence-badge]][licence]\n[![GitHub Last Commit][repo-badge]][repo]\n[![GitHub Issues][issues-badge]][issues]\n[![Python Version][version-badge]][pypi]\n\n```shell\npip install django-settings-holder\n```\n\n---\n\n**Documentation**: [https://mrthearman.github.io/django-settings-holder/](https://mrthearman.github.io/django-settings-holder/)\n\n**Source Code**: [https://github.com/MrThearMan/django-settings-holder/](https://github.com/MrThearMan/django-settings-holder/)\n\n---\n\nThis library provides utilities for Django extensions that want to define their own settings dictionaries.\nSettings can be included in a SettingsHolder that allows them to be accessed via attributes.\nUser defined settings can be reloaded automatically to the SettingsHolder from the `setting_changed` signal.\nFunctions in dot import notation are automatically imported so that the imported function is available in\nthe SettingsHolder.\n\n\n[coverage-badge]: https://coveralls.io/repos/github/MrThearMan/django-settings-holder/badge.svg?branch=main\n[status-badge]: https://img.shields.io/github/workflow/status/MrThearMan/django-settings-holder/Tests\n[pypi-badge]: https://img.shields.io/pypi/v/django-settings-holder\n[licence-badge]: https://img.shields.io/github/license/MrThearMan/django-settings-holder\n[repo-badge]: https://img.shields.io/github/last-commit/MrThearMan/django-settings-holder\n[issues-badge]: https://img.shields.io/github/issues-raw/MrThearMan/django-settings-holder\n[version-badge]: https://img.shields.io/pypi/pyversions/django-settings-holder\n\n[coverage]: https://coveralls.io/github/MrThearMan/django-settings-holder?branch=main\n[status]: https://github.com/MrThearMan/django-settings-holder/actions/workflows/main.yml\n[pypi]: https://pypi.org/project/django-settings-holder\n[licence]: https://github.com/MrThearMan/django-settings-holder/blob/main/LICENSE\n[repo]: https://github.com/MrThearMan/django-settings-holder/commits/main\n[issues]: https://github.com/MrThearMan/django-settings-holder/issues',
    'author': 'Matti Lamppu',
    'author_email': 'lamppu.matti.akseli@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrThearMan/django-settings-holder',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
