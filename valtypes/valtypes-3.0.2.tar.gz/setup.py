# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['valtypes',
 'valtypes.parsing',
 'valtypes.parsing.parser',
 'valtypes.type',
 'valtypes.util']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'valtypes',
    'version': '3.0.2',
    'description': 'Parsing in Python has never been easier',
    'long_description': '<p align="center">\n  <img src="https://github.com/LeeeeT/valtypes/blob/main/docs/logo.svg" />\n</p>\n\n<p align="center">\n    <em>Nothing (almost) should ever be <b>any str</b> or <b>any int</b></em>\n</p>\n\n<p align="center">\n    <a href="https://pypi.org/project/valtypes">\n        <img src="https://img.shields.io/pypi/v/valtypes" />\n    </a>\n    <a href="https://python.org/downloads">\n        <img src="https://img.shields.io/pypi/pyversions/valtypes.svg" />\n    </a>\n    <a href="https://pepy.tech/project/valtypes">\n        <img src="https://img.shields.io/pypi/dm/valtypes" />\n    </a>\n    <a href="https://github.com/LeeeeT/valtypes/actions/workflows/ci.yml">\n        <img src="https://img.shields.io/github/workflow/status/LeeeeT/valtypes/CI" />\n    </a>\n    <a href="https://valtypes.readthedocs.io/en/latest/?badge=latest">\n        <img src="https://img.shields.io/readthedocs/valtypes" />\n    </a>\n    <a href="https://codecov.io/gh/LeeeeT/valtypes">\n        <img src="https://img.shields.io/codecov/c/github/LeeeeT/valtypes" />\n    </a>\n</p>\n\n\n---\n\n\n## What is Valtypes\n\n**Valtypes** is a flexible data parsing library which will help you make illegal states unrepresentable and enable you to practice ["Parse, don’t validate"][parse-dont-validate] in Python. It has many features that might interest you, so let\'s dive into some examples.\n\n\n## Examples\n\nCreate constrained types:\n\n```python\nfrom typing import Generic, TypeVar\n\nfrom valtypes import Constrained\n\n\nT = TypeVar("T")\n\n\nclass NonEmptyList(Constrained[list[T]], list[T], Generic[T]):\n    __constraint__ = bool\n\n\ndef head(l: NonEmptyList[T]) -> T:\n    return l[0]\n\n\nhead(NonEmptyList([1, 2, 3]))  # passes\nhead(NonEmptyList([]))  # runtime error\nhead([1, 2, 3])  # fails at static type checking\n```\n\nParse complex data structures:\n\n```python\nfrom dataclasses import dataclass, field\n\nfrom valtypes import parse, Alias\nfrom valtypes.type.numeric import PositiveInt\n\n\n@dataclass\nclass User:\n    id: PositiveInt = field(metadata=Alias("uid"))\n    name: str\n    hobbies: NonEmptyList[str]\n\n\nraw = {"uid": "1", "name": "Fred", "hobbies": ("origami", "curling", 69)}\n\nprint(parse(User, raw))\n```\n\n```\nUser(id=1, name=\'Fred\', hobbies=[\'origami\', \'curling\', \'69\'])\n```\n\nGet a nice error message if something went wrong:\n\n```python\nraw = {"uid": "-1", "hobbies": ()}\n\nprint(parse(User, raw))\n```\n\n```\nvaltypes.error.CompositeParsingError: User\n├ object 〉 User: not an instance of User\n╰ dict[str, object] 〉 User: User\n  ├ [id]: PositiveInt\n  │ ├ object 〉 PositiveInt: not an instance of PositiveInt\n  │ ╰ int 〉 PositiveInt: the value does not match the PositiveInt constraint\n  ├ [name]: required field is missing\n  ╰ [hobbies]: NonEmptyList[str]\n    ├ object 〉 NonEmptyList[str]: not an instance of NonEmptyList[str]\n    ╰ list[str] 〉 NonEmptyList[str]: the value does not match the NonEmptyList constraint\n```\n\n\n## Installation\n\n```console\npip install valtypes\n```\n\n\n[parse-dont-validate]: https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate\n',
    'author': 'LeeeeT',
    'author_email': 'leeeet@inbox.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/LeeeeT/valtypes',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
