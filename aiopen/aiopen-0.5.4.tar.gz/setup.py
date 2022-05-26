# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['aiopen']

package_data = \
{'': ['*']}

install_requires = \
['funkify>=0.4.0,<0.5.0', 'xtyping>=0.5.0']

setup_kwargs = {
    'name': 'aiopen',
    'version': '0.5.4',
    'description': 'Async file io',
    'long_description': '<a href="https://github.com/dynamic-graphics-inc/dgpy-libs">\n<img align="right" src="https://github.com/dynamic-graphics-inc/dgpy-libs/blob/main/docs/images/dgpy_banner.svg?raw=true" alt="drawing" height="120" width="300"/>\n</a>\n\n# aiopen\n\n[![Wheel](https://img.shields.io/pypi/wheel/aiopen.svg)](https://img.shields.io/pypi/wheel/aiopen.svg)\n[![Version](https://img.shields.io/pypi/v/aiopen.svg)](https://img.shields.io/pypi/v/aiopen.svg)\n[![py_versions](https://img.shields.io/pypi/pyversions/aiopen.svg)](https://img.shields.io/pypi/pyversions/aiopen.svg)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n**Install:** `pip install aiopen`\n\nAsync-open\n\n**Why not use aiofiles?**\n\n - Wanted more type annotations\n - aiofiles uses ye ole `@coroutine` decorator -- aiopen uses python3.6+ `async/await`\n - aiopen is a callable module, so you can do:\n \t- `import aiopen`\n \t- `async with aiopen(\'afile.txt\', \'w\') as f: await f.write(\'some text!\')`\n \t- `async with aiopen(\'afile.txt\', \'r\') as f: content = await f.read()`\n\n\n(Big shouts out to the aiofiles people, aiopen is entirely based off of aiofiles)\n\n\n## Usage:\n\nJust import it! The module is also callable!\n\n```python\nimport aiopen\n\nasync with aiopen(\'afile.txt\', \'w\') as f:\n    await f.write(\'some text!\')\n\nasync with aiopen(\'afile.txt\', \'r\') as f:\n    content = await f.read()\n    print(content)\n\n```\n',
    'author': 'jesse',
    'author_email': 'jesse@dgi.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dynamic-graphics-inc/dgpy-libs/tree/main/libs/aiopen',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
