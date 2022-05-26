# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kare']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'kare',
    'version': '0.0.1',
    'description': 'Minimalist Currying implementation for Python',
    'long_description': "# kare\nMinimal implementation of [Function Currying](https://en.wikipedia.org/wiki/Currying) for python. \n\n## Usage\nYou can curry any callable by applying the `curry` function to it:\n```python\nfrom kare import curry\n\ndef my_sum(x: int, y: int, z: int) -> int:\n    return x + y + z\n\ncurried_sum = curry(my_sum)\n```\n\nCurried functions take a single argument and return either a new function that takes a single argument or the result of applying all the arguments passed so far to the original function:\n```python\nsum_two = curried_sum(2)\nsum_five = sum_two(3)\nsum_five(1) # == 6, equivalent to my_sum(2, 3, 1)\n```\n\nIf you chain multiple calls together for a more succint notation:\n```python\nsum_five = curried_sum(2)(3)\n```\n\nThe `curry` function also works as a decorator:\n```python\n@curry\ndef my_curried_sum(x: int, y: int, z: int) -> int:\n    return x + y + z\n\nadd_six = my_curried_sum(2)(4)\n```\n\nCurrently we only support functions with positional and specified number of arguments. The following:\n```python\n@curry  # This wil raise an exception\ndef variadic_positional_function(*args):\n    ...\n\n@curry # This wil raise an exception\ndef variadic_positional_function(*, x: int, y: int):\n    ...\n\n@curry # This wil raise an exception\ndef variadic_positional_function(x: int, y: int, **kwargs):\n    ...\n\n```\n\nIf you need to do partial application on keyword arguments you can use `functools`' `partial` as usual.",
    'author': 'Francisco J. Jurado',
    'author_email': '9376816+Beetelbrox@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Beetelbrox/kare',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
