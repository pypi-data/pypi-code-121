# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['importsinjson']

package_data = \
{'': ['*']}

extras_require = \
{'commentjson': ['commentjson>=0.9.0,<0.10.0'],
 'pyjson5': ['pyjson5>=1.6.1,<2.0.0']}

setup_kwargs = {
    'name': 'importsinjson',
    'version': '0.1.0',
    'description': 'Adding import functionality to JSON files',
    'long_description': '# ImportsInJSON\n\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![GitHub license](https://img.shields.io/github/license/NathanVaughn/importsinjson)](https://github.com/NathanVaughn/importsinjson/blob/master/LICENSE)\n[![PyPi versions](https://img.shields.io/pypi/pyversions/importsinjson)](https://pypi.org/project/importsinjson)\n[![PyPi downloads](https://img.shields.io/pypi/dm/importsinjson)](https://pypi.org/project/importsinjson)\n\nPython JSON Import Library\n\n---\n\nImportsInJSON is an easy way to allow Python to load JSON files that import data\nfrom other JSON files. This is very helpful for splitting up large JSON files\ninto smaller chunks that can still be combined.\n\n## Installation\n\nImportsInJSON requires Python 3.7+.\n\n```bash\npip install importsinjson\n```\n\nIf you\'d like to support loading JSON files with comments, either add\nthe [`commentjson`](https://pypi.org/project/commentjson/) or\n[`pyjson5`](https://pypi.org/project/pyjson5/) extra when installing.\n\n```bash\npip install importsinjson[commentjson]\n# or\npip install importsinjson[pyjson5]\n```\n\n## Usage\n\nIn your Python code, `import importsinjson` is a drop-in replacement for the\n[`json`](https://docs.python.org/3/library/json.html) module.\n\nIn your JSON document, there are 2 ways to import data from other JSON files.\n\nThe first way is to simply have a key called `$import` with a string value\nthat points to another file. Let\'s say you have a JSON file `a.json`:\n\n```json\n{\n  "name": "John Doe",\n  "age": 30,\n  "$import": "b.json"\n}\n```\n\nand\n\n```json\n{\n  "profession": "Engineer"\n}\n```\n\nRunning `importsinjson.load(\'a.json\')` will return the following:\n\n```json\n{\n  "name": "John Doe",\n  "age": 30,\n  "profession": "Engineer"\n}\n```\n\nThis does observe Python\'s dictionary merging rules, so any keys in the imported\nJSON file that are also in the original document will replace the values in the\noriginal document.\n\nThe second way to import data is to have a string value that starts with `$import:`\nand has the path to the file to import. Modifying the example from before, `a.json`\nwould become\n\n```json\n{\n  "name": "John Doe",\n  "age": 30,\n  "profession": "$import:b.json"\n}\n```\n\nHowever this would load the following:\n\n```json\n{\n  "name": "John Doe",\n  "age": 30,\n  "profession": {\n    "profession": "Engineer"\n  }\n}\n```\n\nTo prevent duplicate keys like this, you can add another `:` after the file path,\nand provide a path to the key in the imported file to use.\n\n```json\n{\n  "name": "John Doe",\n  "age": 30,\n  "profession": "$import:b.json:/profession/"\n}\n```\n\nThis value can be anywhere in the JSON document, including in a list:\n\n```json\n{\n  "name": "John Doe",\n  "age": 30,\n  "professions": ["$import:b.json", "$import:c.json"]\n}\n```\n\n## Options\n\nDepending on the JSON parsing backend selected, options do vary.\nHowever, for all backends, the following options are available:\n\n- `strict`: Defaults to `False`. If `True`, will raise a `FileNotFoundError`\n  if the imported filepath cannot be found. Additionally, if the specified key/index\n  could not be found, the `KeyError`, `IndexError`, etc will be raised. If `False`,\n  the original value will be kept instead.\n\n### Default\n\nThe default JSON parsing backend is the Python standard library `json` module.\nAll normal options for this can be used.\n\n### CommentJSON\n\n[Homepage](https://commentjson.readthedocs.io/en/latest/)\n\n```bash\npip install importsinjson[commentjson]\n```\n\nIf installed, `commentjson` will be used as the JSON parsing backend.\nThis is a pure-Python implementation that strips comments from JSON data before\nhanding them to the `json` module. This also supports all options of the `json` module.\nHowever, it does not support multi-line comments.\n\n### PyJSON5\n\n[Homepage](https://pyjson5.readthedocs.io/en/latest/)\n\n```bash\npip install importsinjson[pyjson5]\n```\n\nLastly, if installed, `pyjson5` will be used as the JSON parsing backend.\nThis is a Cython implementation that loads JSON data with comments. This is the most\nrestrictive backend, with very basic options.\nSee [here](https://pyjson5.readthedocs.io/en/latest/decoder.html#pyjson5.load)\nWhen using this, you may need to explictly add `encoding="utf-8"` to the `load` and\n`loads` functions.\n\nIf for some reason you want to change the prefix used to import data, you can set\nthat like so:\n\n```python\nimport importsinjson\nimportsinjson.PREFIX = "$newimportsymbol"\n```\n\n## Gotchas\n\nUsing the `load` function is much preferred over the `loads` function.\nThis is because with a file handle, the path of the file can be used as an additional\nsearch directory when looking for imported files.\n\nWith `load` imported file paths can be either:\n\n- absolute\n- relative to the parent file\n- relative to the current working directory\n\nWith `loads` imported file paths can only be:\n\n- absolute\n- relative to the current working directory\n\nAdditionally, this module also works recursively, so make sure not to create an\ninfinite loop.\n',
    'author': 'Nathan Vaughn',
    'author_email': 'nvaughn51@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NathanVaughn/importsinjson',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
