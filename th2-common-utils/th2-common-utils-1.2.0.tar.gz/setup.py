# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['th2_common_utils', 'th2_common_utils.util']

package_data = \
{'': ['*']}

install_requires = \
['sortedcollections>=2.0.0,<3.0.0', 'th2-grpc-common>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'th2-common-utils',
    'version': '1.2.0',
    'description': 'Python library with useful functions for developers and QA needs',
    'long_description': "# th2-common-utils-py\nPython library with useful functions for **developers and QA needs**.\n\n## Installation\n```\npip install th2-common-utils\n```\n\n## Usage\n### 1. Message fields access \n\nThe library provides a convenient way for Message fields access.\n\nInstead of this:\n```python\nmsg.fields['BO5Items'].list_value.values[0].message_value.fields['segment_instance_number'].message_value.fields['segment_number'].simple_value\n```\nYou can do this:\n```python\nimport th2_common_utils\n\nmsg['BO5Items'][0]['segment_instance_number']['segment_number']\n```\n\n### 2. Converters\n\n* `message_to_dict(message)` - note, you will lose all metadata of the Message.\n* `dict_to_message(fields, session_alias, message_type)` - where:\n    * *fields* - required argument - message fields as a python dict;\n    * *session_alias* and *message_type* - optional arguments - used to generate message metadata.\n* `dict_to_root_message_filter(message_type, message_filter, metadata_filter, ignore_fields, check_repeating_group_order,\ntime_precision, decimal_precision)` - all arguments are optional.\n* `message_to_typed_message(message, message_type)` - where:\n    * *message* - Message object;\n    * *message_type* - TypedMessage **class object**.\n* `message_to_table(message)` - where:\n    * *message* - Message object or dict.\n\nTo import functions above:\n```python\nfrom th2_common_utils import message_to_dict, dict_to_message # ...\n```\n\n### 3. Working with events\n\n`th2-common-utils` provides the class to work with events - `EventUtils`.\n\nMethods of `EventUtils` class:\n* `create_event_body(component)` - creates event body from `component` as bytes.\n* `create_event_id()` - creates EventID.\n* `create_event(id, parent_id, start_timestamp, end_timestamp, status, name, \ntype, body, attached_message_ids)` - creates event; all arguments are optional.\n\nTo use functions above:\n```python\nfrom th2_common_utils import EventUtils as eu\n\nmy_event = eu.create_event(id=eu.create_event_id,\n                           name='My event',\n                           #... )\n```\n",
    'author': 'TH2-devs',
    'author_email': 'th2-devs@exactprosystems.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/th2-net/th2-common-utils-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
