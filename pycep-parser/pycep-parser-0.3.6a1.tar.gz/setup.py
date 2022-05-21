# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycep']

package_data = \
{'': ['*']}

install_requires = \
['lark>=1.1.2', 'regex>=2022.1.18', 'typing-extensions>=3.10.0']

extras_require = \
{':python_version < "3.9"': ['importlib-resources>=2.0.0']}

setup_kwargs = {
    'name': 'pycep-parser',
    'version': '0.3.6a1',
    'description': 'A Python based Bicep parser',
    'long_description': '# pycep\n\n[![Build Status](https://github.com/gruebel/pycep/workflows/CI/badge.svg)](https://github.com/gruebel/pycep/actions)\n[![codecov](https://codecov.io/gh/gruebel/pycep/branch/master/graph/badge.svg?token=49WHVYGE1D)](https://codecov.io/gh/gruebel/pycep)\n[![PyPI](https://img.shields.io/pypi/v/pycep-parser)](https://pypi.org/project/pycep-parser/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pycep-parser)](https://github.com/gruebel/pycep)\n![CodeQL](https://github.com/gruebel/pycep/workflows/CodeQL/badge.svg)\n\nA parser for [Azure Bicep](https://github.com/Azure/bicep) files leveraging [Lark](https://github.com/lark-parser/lark).\n\nThis is still an early stage, therefore a lot can and will change.\n\n## Getting Started\n\n### Requirements\n\n- Python 3.7+\n- Lark 1.1.2+\n\n### Install\n\n```shell\npip install --upgrade pycep-parser\n```\n\n## Current capabilities\n\n[Supported capabilities](docs/capabilities.md)\n\n## Next milestones\n\n### Functions\n- [x] Any\n- [ ] Array (in progress)\n- [x] Date\n- [x] Deployment\n- [x] File\n- [x] Logical\n- [x] Numeric\n- [x] Object\n- [x] Resource\n- [x] Scope\n- [x] String\n\n### Operators\n- [ ] Accessor\n- [x] Numeric\n\n### CI/CD\n- [ ] Fix security issues found by Scorecard\n\n### Considering\n- 1st class support of interpolated strings\n- Adding line numbers to other parts\n\n### Out-of-scope\n- Bicep to ARM converter and vice versa\n\n## Contributing\n\nFurther details can be found in the [contribution guidelines](CONTRIBUTING.md).\n',
    'author': 'Anton Grübel',
    'author_email': 'anton.gruebel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gruebel/pycep',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
