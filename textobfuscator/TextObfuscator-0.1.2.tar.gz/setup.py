# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['textobfuscator', 'textobfuscator.auxiliary', 'textobfuscator.processor']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'textobfuscator',
    'version': '0.1.2',
    'description': 'Text obfuscator.',
    'long_description': '## Text Obfuscator\n\nObfuscate your message with [Text Obfuscator]()\n\n[![CI](https://github.com/luxiaba/TextObfuscator/actions/workflows/ci.yaml/badge.svg)](https://github.com/luxiaba/textobfuscator/actions/workflows/ci.yaml)\n[![PyPI](https://img.shields.io/pypi/v/TextObfuscator?color=blue&label=PyPI)](https://pypi.org/project/textobfuscator/)\n[![Python 3.8.7](https://img.shields.io/badge/python-3.8.7-blue.svg)](https://www.python.org/downloads/release/python-387/)\n[![codecov](https://codecov.io/gh/luxiaba/TextObfuscator/branch/main/graph/badge.svg?token=WlaPtdYdpg)](https://codecov.io/gh/luxiaba/textobfuscator)\n\n\n### Installation\n```\npip install -U textobfuscator\n```\n\n### Usage\n\n```python\nimport random\nfrom textobfuscator.obfuscator import TextObfuscator\n\n# 1. Replace char.\n# First, now we define rules: replace chars groups.\nCHARS_GROUPS_SOURCE_MAP = (\n  ["😯", "🤣"],\n  ["❌", "✅"],\n)\n\n# 2. Format(Optional)\n# Second, let\'s make some rules to fill the vars that we inserted.\nFORMAT_PREFIX_RULES = {\n  "fake_name": lambda: random.choice(("John", "Min", "William")),\n  "random_weather": lambda: random.choice(("cloudy", "rainy", "sunny", "windy"))\n}\n\nobfuscator = TextObfuscator(\n   replace_source_map=CHARS_GROUPS_SOURCE_MAP,\n   format_prefix_rules=FORMAT_PREFIX_RULES,\n)\n```\n\nNow we have an instance of `TextObfuscator`: `obfuscator`, let\'s do some obfuscations.\n\n```python\nfrom textobfuscator.processor import BreakWord, ObfuscationConfig, Replace\n\n# For each obfuscation, we may specify different rules, such as controls for different words or the number of substitutions, so we make rule here first.\nBREAK_WORDS_RULES = [\n   # We break the word `hello` twice, and put `*` into the middle, like `h*el*lo`\n   BreakWord(word="hello", places=2, fill="*"),\n   # We break the word `world` once, and put `-` into the middle, like `wor-ld`\n   BreakWord(word="world", places=1, fill="-"),\n]\nOBFUSCATOR_CONFIG = ObfuscationConfig(\n   # During the entire obfuscation process, we only replace 1 times.\n   replaces=Replace(count=1),\n   break_words=BREAK_WORDS_RULES,\n)\n\n# OK, let\'s do the obfuscation.\n\n>>> original1 = "hello world!"\n>>> obfuscated = obfuscator.obfuscate(original1, config=OBFUSCATOR_CONFIG)\n>>> print(obfuscated)\n>>> h*ell*o wor-ld!\n\n>>> original2 = "❌ hi {fake_name}, today\'s weather is {random_weather} 😯"\n\n>>> obfuscated = obfuscator.obfuscate(original2, config=OBFUSCATOR_CONFIG)\n>>> print(obfuscated)\n>>> ❌ hi John, today\'s weather is windy 🤣\n\n# Once more.\n>>> obfuscated = obfuscator.obfuscate(original2, config=OBFUSCATOR_CONFIG)\n>>> print(obfuscated)\n>>> ✅ hi Min, today\'s weather is sunny 😯\n```\n\n## Obfuscation Detail\n1. Split content into segments by every args position.\n2. Break words.\n   1. Break words on each segment.\n   2. Merge all segments and put back all key args in places.\n3. Replace.\n   1. Temporarily remove all key args.\n   2. Replace matching chars according to the given mapping table and config.\n   3. Put back all key args that removed on above in places.\n4. Format.\n   1. Merge the `pre-defined` key args and given key args.\n      Here `pre-defined` args means we can create custom var generation rules.\n      For example, we can pass config like below to let all vars stars wth `digit` to autofill in with a real digit, and all vars starts with `letter` to autofill in with a real letter.\n      And the var with the same name will also be filled with the same value.\n      ```python\n      # config\n      # {\n      #     "digit": lambda: random.choice(string.digits),\n      #     "letter": lambda: random.choice(string.ascii_letters),\n      # }\n\n      # before\n      >>> "{digit1} {digit2} {letter2} {digit2}"\n      # after\n      >>> 8 6 z 6\n      ```\n   2. Format and return the content.\n      Put all args we get to the content, and keep those unknown args in original place.\n',
    'author': 'fishermanadg',
    'author_email': 'fishermanadg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/luxiaba/TextObfuscator',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8.7,<4.0.0',
}


setup(**setup_kwargs)
