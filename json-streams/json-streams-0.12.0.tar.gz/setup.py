# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['json_streams',
 'json_streams.backends',
 'json_streams.encoders',
 'json_streams.utility']

package_data = \
{'': ['*']}

install_requires = \
['ijson>=3.1.4,<4.0.0']

extras_require = \
{'orjson': ['orjson>=3.6,<4.0']}

setup_kwargs = {
    'name': 'json-streams',
    'version': '0.12.0',
    'description': 'Stream JSON and JSON-Lines lazily.',
    'long_description': '# json-streams\n\n[![codecov](https://codecov.io/gh/spraakbanken/json-streams-py/branch/master/graph/badge.svg)](https://codecov.io/gh/spraakbanken/json-streams-py/)\n[![Build & Publish](https://github.com/spraakbanken/json-streams-py/workflows/Build%20&%20Publish/badge.svg)](https://github.com/spraakbanken/json-streams-py/actions)\n[![PyPI status](https://badge.fury.io/py/json-streams.svg)](https://pypi.org/project/json-streams/)\n\nRead and write JSON lazy, especially json-arrays.\n\nHandles both the JSON format:\n\n```json\n[\n  {\n    "a": 1\n  },\n  {\n    "a": 2\n  }\n]\n```\n\nAs well as JSON LINES format:\n\n```json\n{"a":1}\n{"a": 2}\n```\n\nAlso supports streaming from gzipped files.\n\nUses `orjson` if present, otherwise standard `json`.\n\n## Usage\n\n### Installation\n\n```bash\n# Using standard json\npip install json-streams\n\n# Using orjson\npip install json-streams[orjson]\n\n```\n\n### Note\n\nThis library prefers files opened in binary mode.\nTherefore does all `dumps`-methods return `bytes`.\n\nAll `loads` methods handles `str`, `bytes` and `bytesarray` arguments.\n\n### Examples\n\nAllows you to use `json.load` and `json.dump` with\nboth json and json-lines files as well as dumping generators.\n\n```python\nimport json_streams\n\n# This command tries to guess format and opens the file\ndata = json_streams.load_from_file("data.json") # or data.jsonl\n\n# Write to file, again guessing format\njson_streams.dump_to_file(data, "data.jsonl")\n```\n\n```python\nfrom json_streams import json_iter, jsonl_iter\n\n# Open and read the file without guessing\ndata = json_iter.load_from_file("data.json")\n\n# Process file\n\n# Write to file without guessing\njsonl_iter.dump_to_file(data, "data.jsonl")\n```\n\n```python\nimport json_streams\ndef process(data):\n    for entry in data:\n        # process\n        yield entry\n\ndef read_process_and_write(filename_in, filename_out):\n\n    json_streams.dump_to_file(\n        process(\n            json_streams.load_from_file(filename_in)\n        ),\n        filename_out\n    )\n```\n\nYou can also use json_streams as a sink, that you can send data to.\n\n```python\nimport json_streams\n\nwith open("out.json", "bw") as fp:\n  # guessing format\n  with json_streams.sink(fp) as sink:\n    for data in data_source():\n      sink.send(data)\n```\n\n# Release Notes\n\n## Latest Changes\n\n## 0.12.0\n\n### Added\n\n- Add support for reading and writing gzipped files. PR [#5](https://github.com/spraakbanken/json-streams-py/pull/5) by [@kod-kristoff](https://github.com/kod-kristoff).\n\n### Changed\n\n- Dropped support for Python 3.6, 3.7 and 3.8.\n\n## 0.11.0\n\n- Allow kwargs to dump\\* methods. PR [#3](https://github.com/spraakbanken/json-streams-py/pull/3) by [@kod-kristoff](https://github.com/kod-kristoff).\n\n\n# Development\n\nAfter cloning the repo, just run\n\n```\n$ make dev\n$ make test\n```\n\nto setup a virtual environment,\ninstall dev dependencies\nand run the unit tests.\n\n_Note:_ If you run the command in a activated virtual environment,\nthat environment is used instead.\n\n# Deployment\n\nPush a tag in the format `v\\d+.\\d+.\\d+`to `main`-branch, to build & publish package to PyPi.\n',
    'author': 'Språkbanken at Göteborgs universitet',
    'author_email': 'sb-info@svenska.gu.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/spraakbanken/json-streams-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
