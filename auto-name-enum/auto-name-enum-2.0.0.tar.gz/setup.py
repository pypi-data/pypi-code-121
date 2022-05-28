# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['auto_name_enum']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'auto-name-enum',
    'version': '2.0.0',
    'description': 'String-based Enum class that automatically assigns values',
    'long_description': '# A utility for producing enums with automatic names\n\nThis package provides an extension of python Enum objects that automatically\nassigns values to members. This uses the `auto()` feature to assign text values\nto the enums instead of having to manually set them.\n\n\n## Specifying your enum\nFor example, you might create an enum with this like so:\n\n```\nclass Pets(AutoNameEnum):\n    DOG = auto()\n    CAT = auto()\n    PIG = auto()\n```\n\n## Getting values\n\nUsing the class, verify the value of `DOG` would be \'dog\':\n\n```\n>>> print(Pets.DOG.value)\n\'DOG\'\n```\n\nYou may also get the same value by just using the name of the item:\n\n```\n>>> print(Pets.DOG)\n\'DOG\'\n```\n\n## Iterating\n\nPython enums may be iterated over:\n\n```\nfor pet in Pets:\n    print(f"name: {pet.name}, value: {pet.value}")\n```\n\nFor more information on enums (and the auto method), see [the official docs]\n(https://docs.python.org/3/library/enum.html)\n',
    'author': 'Tucker Beck',
    'author_email': 'tucker.beck@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dusktreader/auto-name-enum',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
