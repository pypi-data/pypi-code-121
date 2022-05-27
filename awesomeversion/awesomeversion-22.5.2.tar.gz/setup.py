# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['awesomeversion', 'awesomeversion.comparehandlers', 'awesomeversion.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'awesomeversion',
    'version': '22.5.2',
    'description': 'One version package to rule them all, One version package to find them, One version package to bring them all, and in the darkness bind them.',
    'long_description': '# AwesomeVersion\n\n[![codecov](https://codecov.io/gh/ludeeus/awesomeversion/branch/main/graph/badge.svg)](https://codecov.io/gh/ludeeus/awesomeversion)\n![python version](https://img.shields.io/badge/Python-3.7=><=3.10-blue.svg)\n![dependencies](https://img.shields.io/badge/Dependencies-0-blue.svg)\n[![PyPI](https://img.shields.io/pypi/v/awesomeversion)](https://pypi.org/project/awesomeversion)\n![Actions](https://github.com/ludeeus/awesomeversion/workflows/Actions/badge.svg?branch=main)\n\n_One version package to rule them all, One version package to find them, One version package to bring them all, and in the darkness bind them._\n\nMake anything a version object, and compare against a vast section of other version formats.\n\n## Installation\n\n```bash\npython3 -m pip install awesomeversion\n```\n\n## AwesomeVersion class\n\nThe AwesomeVersion class takes a version as the first argument, you can also pass in additional arguments to customize the version object.\n\nArgument | Description\n--- | ---\n`version` | The version string to parse.\n`ensure_strategy` | Match the `AwesomeVersion` object against spesific strategies when creating if. If it does not match `AwesomeVersionStrategyException` will be raised\n`find_first_match` | If True, the version given will be scanned for the first match of the given `ensure_strategy`. Raises `AwesomeVersionStrategyException` If it is not found for any of the given strategies.\n\n\n## Example usage\n\nThese are some examples of what you can do, more examples can be found in the `tests` directory.\n\n```python\nfrom awesomeversion import AwesomeVersion\n\ncurrent = AwesomeVersion("1.2.2")\nupstream = AwesomeVersion("1.2.3")\n\nprint(upstream > current)\n> True\n```\n\n```python\nfrom awesomeversion import AwesomeVersion\n\nversion = AwesomeVersion("1.2.3b0")\n\nprint(version.beta)\n> True\n```\n\n```python\nfrom awesomeversion import AwesomeVersion\n\ncurrent = AwesomeVersion("2021.1.0")\nupstream = AwesomeVersion("2021.1.0b2")\n\nprint(upstream > current)\n> False\n```\n\n```python\nfrom awesomeversion import AwesomeVersion\n\ncurrent = AwesomeVersion("latest")\nupstream = AwesomeVersion("2021.1.0")\n\nprint(upstream > current)\n> False\n```\n\n```python\nfrom awesomeversion import AwesomeVersion\n\ncurrent = AwesomeVersion("latest")\nupstream = AwesomeVersion("dev")\n\nprint(upstream > current)\n> True\n```\n\n```python\nfrom awesomeversion import AwesomeVersion\n\nwith AwesomeVersion("20.12.0") as current:\n    with AwesomeVersion("20.12.1") as upstream:\n        print(upstream > current)\n> True\n```\n\n```python\nfrom awesomeversion import AwesomeVersion\n\nwith AwesomeVersion("20.12.0") as current:\n    print("2020.12.1" > current)\n> True\n```\n\n```python\nfrom awesomeversion import AwesomeVersion\n\nversion = AwesomeVersion("2.12.0")\nprint(version.major)\n> 2\nprint(version.minor)\n> 12\nprint(version.patch)\n> 0\n```\n\n## Contribute\n\n**All** contributions are welcome!\n\n1. Fork the repository\n2. Clone the repository locally and open the devcontainer or use GitHub codespaces\n3. Do your changes\n4. Lint the files with `make lint`\n5. Ensure all tests passes with `make test`\n6. Ensure 100% coverage with `make coverage`\n7. Commit your work, and push it to GitHub\n8. Create a PR against the `main` branch\n',
    'author': 'Ludeeus',
    'author_email': 'ludeeus@ludeeus.dev',
    'maintainer': 'Ludeeus',
    'maintainer_email': 'ludeeus@ludeeus.dev',
    'url': 'https://github.com/ludeeus/awesomeversion',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
