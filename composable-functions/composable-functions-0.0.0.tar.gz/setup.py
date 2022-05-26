# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['composable']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'composable-functions',
    'version': '0.0.0',
    'description': 'Function composition in python',
    'long_description': '# Composable functions\nF#-style function composition for Python. Compose functions using bitshift operators `>>` & `<<`\n## Installation\nTBD\n\n## Usage\nYou can wrap any `Callable` with `composable` to make it a composable function. Composable functions can be composed with other `Callable` objects using the bit shift operators (`<<` & `>>`):\n```python\nfrom composable.functions import composable as c\n\ndef add_one(x: int) -> int:\n    return x + 1\n\ndef add_two(x: int) -> int:\n    return x + 2\n\nc_add_one = c(add_one)\nc_add_two = c(add_two)\n\n# You can compose with other composables:\nadd_three = c_add_one >> c_add_two\n# Equivalent to:\n# add_three = lambda x: add_two(add_one(x))\nadd_three(5)  # == 8\n\n# Or with any `Callable` object\nadd_five = c_add_one >> add_two >> add_two\n# Equivalent to:\n# add_five = lambda x: add_two(add_two(add_one(x)))\nadd_five(5)  # == 10\n```\nIt also works as a decorator:\n```python\nfrom composable.functions import composable\n\n@composable\ndef add_one(x: int) -> int:\n    return x + 1\n\nadd_three = add_one >> add_one >> add_one\n```\nComplex pipelines can be built by reusing simple functions:\n```python\nfrom composable.functions import compose\nimport io\n\nfake_stream\nword_counter = (\n    I >> str.strip\n    >> str.split\n    >> len\n)\nword_counter(line) == 6\n```\n\nYou can also compose multiple functions at once with `compose`:\n\nThis can be useful to programatically build complex functions\n',
    'author': 'Francisco J. Jurado Moreno',
    'author_email': '9376816+Beetelbrox@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
