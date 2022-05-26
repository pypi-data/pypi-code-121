# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['task_script_utils',
 'task_script_utils.datetime_parser',
 'task_script_utils.datetime_parser.utils']

package_data = \
{'': ['*'], 'task_script_utils.datetime_parser': ['flowcharts/*']}

install_requires = \
['arrow>=1.2.2,<2.0.0',
 'dateparser>=1.1.1,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'pydash>=5.1.0,<6.0.0',
 'python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'ts-task-script-utils',
    'version': '1.3.0',
    'description': 'Python utility for Tetra Task Scripts',
    'long_description': '# ts-task-script-utils <!-- omit in toc -->\n\n[![Build Status](https://travis-ci.com/tetrascience/ts-task-script-utils.svg?branch=master)](https://travis-ci.com/tetrascience/ts-task-script-utils)\n\nUtility functions for Tetra Task Scripts\n\n- [Installation](#installation)\n- [Usage](#usage)\n- [Datetime Parser](#datetime-parser)\n- [Test](#test)\n- [Changelog](#changelog)\n  - [v1.2.0](#v120)\n  - [v1.1.1](#v111)\n  - [v1.1.0](#v110)\n\n## Installation\n\n`pip install ts-task-script-utils`\n\n## Usage\n\n`from task_script_utils.is_number import isnumber`\n\n`print(isnumber(\'a\'))`\n\n## Datetime Parser\n\n```python\nfrom task_script_utils.datetime_parser import parse\n\nparse("2004-12-23T12:30 AM +05:30")\nparse("2004-12-23T12:30 AM +05:30", <datetime_config>)\nparse("2004-12-23T12:30 AM +05:30", <format_list>)\nparse("2004-12-23T12:30 AM +05:30", <format_list>, <datetime_config>)\n```\n\n`parse()` returns a `TSDatetime` Object. You can use `TSDatetime.tsformat()` and\n`TSDatetime.isoformat()` to get datetime string. You can also use\n`TSDatetime.datetime()` to access python datetime object.\n\nYou can read more about the datetime parser [here](task_script_utils/datetime_parser/README.md).\n\n\n## Changelog\n\n### v1.3.0\n\n - Added string parsing functions\n\n### v1.2.0\n\n- Add boolean config parameter `require_unambiguous_formats` to `DatetimeConfig`\n- Add logic to `parser._parse_with_formats` to be used when `DatetimeConfig.require_unambiguous_formats` is set to `True`\n  - `AmbiguousDatetimeFormatsError` is raised if mutually ambiguous formats are detected and differing datetimes are parsed\n- Add parameter typing throughout repository\n- Refactor `datetime_parser` package\n- Add base class `DateTimeInfo`\n- Segregate parsing logic into `ShortDateTimeInfo` and `LongDateTimeInfo`\n\n### v1.1.1\n\n- Remove `convert_to_ts_iso8601()` method\n\n### v1.1.0\n\n- Add `datetime_parser` package\n',
    'author': 'Tetrascience',
    'author_email': 'developers@tetrascience.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
