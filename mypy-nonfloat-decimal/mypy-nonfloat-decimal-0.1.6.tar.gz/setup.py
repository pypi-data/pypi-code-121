# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mypy_nonfloat_decimal']

package_data = \
{'': ['*']}

install_requires = \
['mypy>=0.720']

setup_kwargs = {
    'name': 'mypy-nonfloat-decimal',
    'version': '0.1.6',
    'description': 'Mypy plugin to prevent passing float type to Decimal to avoid imprecisions.',
    'long_description': '# Mypy non-float Decimal plugin\n\nRestricts passing float numbers to Decimal\n\n## Why?\n\n[The implementation of floating point numbers](https://docs.python.org/3/tutorial/floatingpoint.html) \ncan cause imprecisions in results. To avoid this problem you can use `Decimal` type, \nhowever you still need to avoid passing `float` as its parameter:\n\n```\n>>> Decimal(1.02)\nDecimal("1.020000000000000017763568394002504646778106689453125")\n>>> Decimal("1.02")\nDecimal("1.02")\n```\n\nThis plugin is meant to spot occurrences where `float` is passed to `Decimal` in your code.\n\n## Usage\n\n- install plugin\n\n```\npip install mypy-nonfloat-decimal\n```\n\n- add it into list of mypy plugins in your mypy config (`mypy.ini`)\n\n```\n[mypy]\nplugins=mypy_nonfloat_decimal\n```\n\n- upon running mypy will detect `float` passed to `Decimal` and report it as an error (`example.py`):\n\n\n```\nfrom decimal import Decimal\nDecimal(1.02)\n```\n\n```\n$ mypy --config-file ./mypy.ini ./example.py\n\nexample.py:2: error: Invalid type passed to Decimal (expected "Union[int, str, Decimal]"), got float instead\n```\n',
    'author': 'yedpodtrzitko',
    'author_email': 'yedpodtrzitko@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
