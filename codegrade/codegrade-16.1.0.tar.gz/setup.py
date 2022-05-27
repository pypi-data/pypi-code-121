# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cg_dt_utils',
 'cg_maybe',
 'cg_request_args',
 'codegrade',
 'codegrade._api',
 'codegrade.models']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.19.0,<1.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'structlog>=20.1.0,<21.0.0',
 'typing-extensions>=3.7.4.3,<4.0.0.0',
 'validate-email>=1.3,<2.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.8,<0.9']}

setup_kwargs = {
    'name': 'codegrade',
    'version': '16.1.0',
    'description': 'A client library for accessing CodeGrade',
    'long_description': '# CodeGrade API\n\nThis library makes it easier to use the CodeGrade API. Its API allows you to\nautomate your usage of CodeGrade. We are currently still busy documenting the\nentire API, but everything that is possible in the UI of CodeGrade is also\npossible through the API.\n## Installation\nYou can install the library through [pypi](https://pypi.org/), simply run\n`python3 -m pip install codegrade`. If you want to get a dev version with support\nfor the latest features, simply email [support@codegrade.com](mailto:support@codegrade.com)\nand we\'ll provide you with a dev version.\n## Usage\nFirst, create a client:\n\n```python\nimport codegrade\n\n# Don\'t store your password in your code!\nwith codegrade.login(\n    username=\'my-username\',\n    password=os.getenv(\'CG_PASSWORD\'),\n    tenant=\'My University\',\n) as client:\n    pass\n\n# Or supply information interactively.\nwith codegrade.login_from_cli() as client:\n    pass\n```\n\nNow call your endpoint and use your models:\n\n```python\nfrom codegrade.models import PatchCourseData\n\ncourses = client.course.get_all()\nfor course in courses:\n    client.course.patch(\n        PatchCourseData(name=course.name + \' (NEW)\'),\n        course_id=course.id,\n    )\n\n# Or, simply use dictionaries.\nfor course in courses:\n    client.course.patch(\n        {"name": course.name + \' (NEW)\'},\n        course_id=course.id,\n    )\n```\n\nFor the complete documentation go to\nhttps://python.api.codegrade.com.\n## Backwards compatibility\nCodeGrade is constantly upgrading its API, but we try to minimize backwards\nincompatible changes. We\'ll announce every backwards incompatible change in the\n[changelog](http://help.codegrade.com/changelog). A new version of the API\nclient is released with every release of CodeGrade, which is approximately every\nmonth. To upgrade simply run `pip install --upgrade codegrade`.\n## Supported python versions\nWe support python 3.6 and above, `pypy` is currently not tested but should work\njust fine.\n## License\nThe library is licensed under AGPL-3.0-only or BSD-3-Clause-Clear.',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
