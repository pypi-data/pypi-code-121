# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipen_filters']

package_data = \
{'': ['*']}

install_requires = \
['pipen>=0.3,<0.4']

entry_points = \
{'pipen': ['filters = pipen_filters:PipenFilters']}

setup_kwargs = {
    'name': 'pipen-filters',
    'version': '0.1.2',
    'description': 'Add a set of useful filters for pipen templates',
    'long_description': '# pipen-filters\n\nAdd a set of useful filters for [pipen][1] templates.\n\nThese filters can be used for both liquid and jinja2 templating in pipen.\n\n## Installation\n\n```\npip install -U pipen-filters\n```\n\n## Enabling/Disabling the plugin\n\nThe plugin is registered via entrypoints. It\'s by default enabled. To disable it:\n`plugins=[..., "no:filters"]`, or uninstall this plugin.\n\n## Usage\n\n```python\nfrom pipen import Proc\n\nclass MyProc(Proc):\n    input = "infile:file"\n    output = "outfile:file:{{in.infile | stem}}.txt"\n    ...\n```\n\n## Filters\n\n- Parse the symbolic links\n\n    - `realpath`: `os.path.realpath`\n    - `readlink`: `os.readlink`\n\n- Find common prefix of given paths\n\n    - `commonprefix`:\n\n        ```python\n        >>> commonprefix("/a/b/abc.txt", "/a/b/abc.png")\n        >>> # "abc."\n        >>> commonprefix("/a/b/abc.txt", "/a/b/abc.png", basename_only=False)\n        >>> # "/a/b/abc."\n        ```\n\n- Get parts of the path\n\n    - `dirname`: `path.dirname`\n    - `basename`: `path.basename`\n    - `ext`: get the extension (`/a/b/c.txt -> .txt`)\n    - `ext0`: get the extension without dot (`/a/b/c.txt -> txt`)\n    - `prefix`: get the prefix of a path (`/a/b/c.d.txt -> /a/b/c.d`)\n    - `prefix0`: get the prefix of a path without dot in basename (`/a/b/c.d.txt -> /a/b/c`)\n    - `filename`, `fn`, `stem`: get the stem of a path (`/a/b.c.txt -> b.c`)\n    - `filename0`, `fn0`, `stem0`: get the stem of a path without dot (`/a/b.c.txt -> b`)\n    - `joinpaths`: join path parts (`os.path.join`)\n    - `as_path`: convert a string into a `pathlib.Path` object\n\n- Quote data\n\n    - `quote`: put double quotes around data (`1 -> "1"`)\n    - `squote`: put single quotes around data (`1 -> \'1\'`)\n\n- Configurations\n    - `json`: `json.dumps`\n    - `json_dump`: Load json froma  file\n    - `json_dumps`: Alias of `json`\n    - `json_loads`: `json.loads`\n    - `toml`: `toml.dumps`\n    - `toml_dump`: Load toml from a file\n    - `toml_dumps`: Alias of `toml`\n    - `toml_loads`: `toml.loads`\n    - `config`: Load configuration from an object, a string or a file\n\n- Globs\n\n    - `glob`: Like `glob.glob`, but allows passing multiple parts of a path\n    - `glob0`: Like `glob`, but only returns the first matched path\n\n- Read file contents\n\n    - `read`: Read file content. You can also pass arguments to `open`\n    - `readlines`: Read file content as a list of lines. Additional arguments will be passed to `open`\n\n\n[1]: https://github.com/pwwang/pipen\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pwwang/pipen-filters',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
