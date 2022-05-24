# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simpleconf', 'simpleconf.loaders']

package_data = \
{'': ['*']}

install_requires = \
['diot>=0.1,<0.2']

extras_require = \
{'all': ['python-dotenv>=0.20,<0.21',
         'pyyaml>=6,<7',
         'rtoml>=0.8,<0.9',
         'iniconfig>=1.1,<2.0'],
 'env': ['python-dotenv>=0.20,<0.21'],
 'ini': ['iniconfig>=1.1,<2.0'],
 'toml': ['rtoml>=0.8,<0.9'],
 'yaml': ['pyyaml>=6,<7']}

setup_kwargs = {
    'name': 'python-simpleconf',
    'version': '0.5.6',
    'description': 'Simple configuration management with python.',
    'long_description': '# simpleconf\n\nSimple configuration management for python\n\n## Installation\n```shell\n# released version\npip install python-simpleconf\n\n# Install support for ini\npip install python-simpleconf[ini]\n\n# Install support for dotenv\npip install python-simpleconf[dotenv]\n\n# Install support for yaml\npip install python-simpleconf[yaml]\n\n# Install support for toml\npip install python-simpleconf[toml]\n\n# Install support for all supported formats\npip install python-simpleconf[all]\n```\n\n## Features\n- Multiple formats supported\n- Type casting\n- Profile support\n- Simple APIs\n\n## Usage\n\n### Loading configurations\n\n```python\nfrom simpleconf import Config\n\n# Load a single file\nconf = Config.load(\'~/xxx.ini\')\n# load multiple files, later files override previous ones\nconf = Config.load(\n   \'~/xxx.ini\', \'~/xxx.env\', \'~/xxx.yaml\', \'~/xxx.toml\',\n   \'~/xxx.json\', \'simpleconf.osenv\', {\'a\': 3}\n)\n\n# Load a single file with a different loader\nconf = Config.load(\'~/xxx.ini\', loader="toml")\n```\n\n### Accessing configuration values\n\n```python\nfrom simpleconf import Config\n\nconf = Config.load({\'a\': 1, \'b\': {\'c\': 2}})\n# conf.a == 1\n# conf.b.c == 2\n```\n\n### Supported formats\n\n- `.ini/.cfg/.config` (parsed by `iniconfig`).\n  - For confiurations without profiles, an ini-like configuration like must have a `default` (case-insensitive) section.\n- `.env` (using `python-dotenv`). A file with environment variables.\n- `.yaml/.yml` (using `pyyaml`). A file with YAML data.\n- `.toml` (using `rtoml`). A file with TOML data.\n- `.json` (using `json`). A file with JSON data.\n- `XXX.osenv`: System environment variables with prefix `XXX_` (case-sensitive) is used.\n  - `XXX_A=1` will be loaded as `conf.A = 1`.\n- python dictionary.\n\n### Profile support\n\n#### Loading configurations\n\n##### Loading dictionaries\n\n```python\nfrom simpleconf import ProfileConfig\n\nconf = ProfileConfig.load({\'default\': {\'a\': 1})\n# conf.a == 1\n```\n\n##### Loading a `.env` file\n\n`config.env`\n```env\n# config.env\ndefault_a=1\n```\n\n```python\nfrom simpleconf import ProfileConfig\n\nconf = ProfileConfig.load(\'config.env\')\n# conf.a == 1\n```\n\n##### Loading ini-like configuration files\n\n```ini\n# config.ini\n[default]\na = 1\n```\n\n```python\nfrom simpleconf import ProfileConfig\n\nconf = ProfileConfig.load(\'config.ini\')\n# conf.a == 1\n```\n\n##### Loading JSON files\n\n`config.json`\n```json\n{\n  "default": {\n    "a": 1\n  }\n}\n```\n\n```python\nfrom simpleconf import ProfileConfig\n\nconf = ProfileConfig.load(\'config.json\')\n# conf.a == 1\n```\n\n##### Loading system environment variables\n\n```python\nfrom os import environ\nfrom simpleconf import ProfileConfig\n\nenviron[\'XXX_DEFAULT_A\'] = \'1\'\n\nconf = ProfileConfig.load(\'XXX.osenv\')\n# conf.a == 1\n```\n\n##### Loading TOML files\n\n```toml\n# config.toml\n[default]\na = 1\n```\n\n```python\nfrom simpleconf import ProfileConfig\n\nconf = ProfileConfig.load(\'config.toml\')\n# conf.a == 1\n```\n\n##### Loading YAML files\n\n```yaml\n# config.yaml\ndefault:\n  a: 1\n```\n\n```python\nfrom simpleconf import ProfileConfig\n\nconf = ProfileConfig.load(\'config.yaml\')\n# conf.a == 1\n```\n\n#### Switching profile\n\n```python\nfrom simpleconf import ProfileConfig\n\nconf = ProfileConfig.load(\n   {\'default\': {\'a\': 1, \'b\': 2}, \'dev\': {\'a\': 3}, \'prod\': {\'a\': 4}}\n)\n# conf.a == 1; conf.b == 2\n# ProfileConfig.profiles(conf) == [\'default\', \'dev\', \'prod\']\n# ProfileConfig.pool(conf) == {\'default\': {\'a\': 1, \'b\': 2}, \'dev\': {\'a\': 3}, \'prod\': {\'a\': 4}}\n# ProfileConfig.current_profile(conf) == \'default\'\n# ProfileConfig.base_profile(conf) == \'default\'\n\nProfileConfig.use_profile(conf, \'dev\')\n# conf.a == 3; conf.b == 2\n# ProfileConfig.current_profile(conf) == \'dev\'\n# ProfileConfig.base_profile(conf) == \'default\'\n\n# use a different base profile\nProfileConfig.use_profile(conf, \'prod\', base=\'dev\')\n# conf.a == 4   # No \'b\' in conf\n# ProfileConfig.current_profile(conf) == \'prod\'\n# ProfileConfig.base_profile(conf) == \'dev\'\n\n# Copy configuration instead of inplace modification\nconf2 = ProfileConfig.use_profile(conf, \'dev\', copy=True)\n# conf2 is not conf\n# conf2.a == 3; conf2.b == 2\n\n# Use a context manager\nwith ProfileConfig.use_profile(conf2, \'default\'):\n    conf2.a == 3\n    conf2.b == 2\n# conf2.a == 3; conf2.b == 2\n```\n\n### Type casting\n\nFor configuration formats with type support, including dictionary, no type casting is done by this library, except that for TOML files.\n\nTOML does not support `None` value in python. We use `rtoml` library to parse TOML files, which dumps `None` as `"null"`. So a `null_caster` is used to cast `"null"` to `None`.\n\nA `none_caster` is also enabled for TOML files, a pure string of `"@none"` is casted to `None`.\n\nFor other formats, following casters are supported:\n\n#### Int caster\n\n```python\nfrom os import environ\nfrom simpleconf import Config\n\nenviron[\'XXX_A\'] = \'@int:1\'\n\nconf = Config.load(\'XXX.osenv\')\n# conf.a == 1 # int\n```\n\n#### Float caster\n\n`@float:1.0` -> `1.0`\n\n### Bool caster\n\n`@bool:true` -> `True`\n`@bool:false` -> `False`\n\n#### Python caster\n\nValues are casted by `ast.literal_eval()`.\n\n```python\n"@python:1" => 1  # or\n"@py:1" => 1\n"@py:1.0` -> `1.0`\n"@py:[1, 2, 3]" => [1, 2, 3]\n```\n\n#### JSON caster\n\n`@json:{"a": 1}` -> `{"a": 1}`\n\n#### TOML caster\n\n`@toml:a = 1` -> `{"a": 1}`\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pwwang/simpleconf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
