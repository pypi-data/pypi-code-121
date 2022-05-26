# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['teslajsonpy', 'teslajsonpy.homeassistant']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'authcaptureproxy>=1.1.3,<2.0.0',
 'backoff>=1.10.0,<2.0.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'httpx>=0.17.1,<1.0',
 'wrapt>=1.12.1,<2.0.0']

setup_kwargs = {
    'name': 'teslajsonpy',
    'version': '2.2.1',
    'description': 'A library to work with Tesla API.',
    'long_description': '# teslajsonpy\n[![Version status](https://img.shields.io/pypi/status/teslajsonpy)](https://pypi.org/project/teslajsonpy)\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n[![Python version compatibility](https://img.shields.io/pypi/pyversions/teslajsonpy)](https://pypi.org/project/teslajsonpy)\n[![Version on Github](https://img.shields.io/github/v/release/zabuldon/teslajsonpy?include_prereleases&label=GitHub)](https://github.com/zabuldon/teslajsonpy/releases)\n[![Version on PyPi](https://img.shields.io/pypi/v/teslajsonpy)](https://pypi.org/project/teslajsonpy)\n![PyPI - Downloads](https://img.shields.io/pypi/dd/teslajsonpy)\n![PyPI - Downloads](https://img.shields.io/pypi/dw/teslajsonpy)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/teslajsonpy)\n\nAsync python module for Tesla API primarily for enabling Home-Assistant.\n\n**NOTE:** Tesla has no official API; therefore, this library may stop\nworking at any time without warning.\n\n# Credits\n\nOriginally inspired by [this code.](https://github.com/gglockner/teslajson)\nAlso thanks to [Tim Dorr](https://tesla-api.timdorr.com/) for documenting the API. Additional repo scaffolding from [simplisafe-python.](https://github.com/bachya/simplisafe-python)\n\n# Contributing\n\n1.  [Check for open features/bugs](https://github.com/zabuldon/teslajsonpy/issues)\n    or [initiate a discussion on one](https://github.com/zabuldon/teslajsonpy/issues/new).\n2.  [Fork the repository](https://github.com/zabuldon/teslajsonpy/fork/new).\n3.  Install the dev environment: `make init`.\n4.  Enter the virtual environment: `poetry shell`\n5.  Code your new feature or bug fix. [Developers Reference](DEVELOPERS.md)\n6.  Write a test that covers your new functionality.\n7.  Update `README.md` with any new documentation.\n8.  Run tests and ensure 100% code coverage for your contribution: `make coverage`\n9.  Ensure you have no linting errors: `make lint`\n10. Ensure you have typed your code correctly: `make typing`\n11. Add yourself to `AUTHORS.md`.\n12. Submit a [pull request](https://github.com/zabuldon/teslajsonpy/pulls)!\n\n# Documentation\n[API docs](https://teslajsonpy.readthedocs.io/en/latest/).\n\n# License\n\n[Apache-2.0](LICENSE). By providing a contribution, you agree the contribution is licensed under Apache-2.0.\nThis code is provided as-is with no warranty. Use at your own risk.\n',
    'author': 'Sergey Isachenko',
    'author_email': 'sergey.isachenkol@bool.by',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zabuldon/teslajsonpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
