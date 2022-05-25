# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_jungle', 'flake8_jungle.rules']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=3.8.4']

entry_points = \
{'flake8.extension': ['JG = flake8_jungle:JungleStyleChecker']}

setup_kwargs = {
    'name': 'flake8-jungle',
    'version': '1.0.3',
    'description': 'Plugin to lint various issues in code.',
    'long_description': '# flake8-jungle\n\nA flake8 plugin to detect bad practices in projects. This plugin is based on [flake8-django](https://github.com/rocioar/flake8-django/).\n\n## Installation\n\nInstall from pip with:\n\n```\n$ pip install flake8-jungle\n```\n\n## `pre-commit` example\n\n```yaml\n  - repo: https://github.com/pycqa/flake8\n    rev: 4.0.1\n    hooks:\n      - id: flake8\n        additional_dependencies: [\'flake8-jungle==VERSION\']\n        args: [\'--max-condition-complexity=8\']\n```\n\n## List of Rules\n\n| Rule | Description | Configuration |\n| ---- | ----------- | ------------- |\n| `JG01` | The order of the model\'s inner classes, methods, and fields does not follow the [Django Style Guide](https://github.com/HackSoftware/Django-Styleguide). | |\n| `JG02` | Do not use `exclude` attribute in `ModelForm`, list all items explicitly in `fields` attribute instead. | |\n| `JG03` | Avoid using `null=True` on string-based fields such as `CharField` and `TextField`. | |\n| `JG04` | Exceptions should never pass silently, add logging or comment at least. | |\n| `JG05` | Condition is too complex which makes it hard to understand. | `--max-condition-complexity` |\n| `JG06` | Function is too long. | `--max-function-length` |\n| `JG07` | Model is too long, split it into services, selectors, or utilities. | `--max-model-length` |\n| `JG08` | Function or method contains local imports, which should be mostly avoided. If you are trying to fix curcular dependency issues, the design probably has some flaws, you should consider refactoring instead. |\n| `JG09` | Incorrect logging format, please use the following syntax: `logging.info("MESSAGE %(arg1)s", {"arg1": "value1"}`) | |\n| `JG10` | Too much patching in tests. Consider changing your design to utilize Dependency Injection and fakes. | `--max-patches-in-test` |\n\n## Testing\n\nflake8-jungle uses pytest for tests. To run them use:\n\n```\n$ poetry install\n$ poetry run pytest tests\n```\n',
    'author': 'Twisto Platform Team',
    'author_email': 'platform@twisto.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TwistoPayments/flake8-jungle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
