# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['impexpr']

package_data = \
{'': ['*']}

install_requires = \
['black>=22.1.0,<23.0.0', 'ideas>=0.0.37,<0.0.38']

entry_points = \
{'console_scripts': ['impexpr = impexpr:main']}

setup_kwargs = {
    'name': 'impexpr',
    'version': '0.0.3',
    'description': 'A simple superset of Python with import expressions added in',
    'long_description': '# Impexpr\nA simple superset of Python with import expressions added in. Beware: This project has only been made as a proof of concept and is not intended to ever be used in production. \n\n## Installation\n```bash\npip install impexpr\n```\n## Quickstart\n* If you wish to import itertools and use it in the same line, run `impexpr` with the file with the following contents as the first argument:\n```python\nfor x in (import itertools).chain([1, 2], [3, 4], [5, 6]):\n    print(x)\n```\n* For everything else, run `impexpr --help`',
    'author': 'Stanislav Zmiev',
    'author_email': 'szmiev2000@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Ovsyanka83/impexpr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
