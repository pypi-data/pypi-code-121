# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uzi', 'uzi._common', 'uzi.graph']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.4.0,<22.0.0',
 'blinker>=1.4,<2.0',
 'typing-extensions>=4.1.1,<5.0.0']

setup_kwargs = {
    'name': 'uzi',
    'version': '0.3.2',
    'description': 'Dependency injection library',
    'long_description': '# Uzi\n\n\n[![PyPi version][pypi-image]][pypi-link]\n[![Supported Python versions][pyversions-image]][pyversions-link]\n[![Build status][ci-image]][ci-link]\n[![Coverage status][codecov-image]][codecov-link]\n\n\n`Uzi` is a [dependency injection](https://en.wikipedia.org/wiki/Dependency_injection) framework for Python.\n\n## Install\n\nInstall from [PyPi](https://pypi.org/project/uzi/)\n\n```\npip install uzi\n```\n\n## Features\n\n- Async support: `uzi` will `await` for you.\n- Lots of Providers to choose from. E.g.\n[Value](https://pyuzi.github.io/uzi/basic/providers/value.html), \n[Alias](https://pyuzi.github.io/uzi/basic/providers/alias.html).\n- Extensibility through `Container` inheritance.\n- Multi scope support.\n- Fast: minus the cost of an additional stack frame, `uzi` resolves dependencies \nnearly as efficiently as resolving them by hand.\n\n\n## Links\n\n- __[Documentation][docs-link]__\n- __[API Reference][api-docs-link]__\n- __[Installation][install-link]__\n- __[Get Started][why-link]__\n- __[Contributing][contributing-link]__\n\n\n\n## Production\n\nThis package is currently under active development and is not recommended for production use.\n\nWill be production ready from version `v1.0.0` onwards.\n\n\n\n[docs-link]: https://pyuzi.github.io/uzi/\n[api-docs-link]: https://pyuzi.github.io/uzi/api/\n[install-link]: https://pyuzi.github.io/uzi/install.html\n[why-link]: https://pyuzi.github.io/uzi/why.html\n[contributing-link]: https://pyuzi.github.io/uzi/0.5.x/contributing.html\n[pypi-image]: https://img.shields.io/pypi/v/uzi.svg?color=%233d85c6\n[pypi-link]: https://pypi.python.org/pypi/uzi\n[pyversions-image]: https://img.shields.io/pypi/pyversions/uzi.svg\n[pyversions-link]: https://pypi.python.org/pypi/uzi\n[ci-image]: https://github.com/pyuzi/uzi/actions/workflows/workflow.yaml/badge.svg?event=push&branch=master\n[ci-link]: https://github.com/pyuzi/uzi/actions?query=workflow%3ACI%2FCD+event%3Apush+branch%3Amaster\n[codecov-image]: https://codecov.io/gh/pyuzi/uzi/branch/master/graph/badge.svg\n[codecov-link]: https://codecov.io/gh/pyuzi/uzi\n\n\nSee this release on GitHub: [v0.3.2](https://github.com/pyuzi/uzi/releases/tag/0.3.2)\n',
    'author': 'David Kyalo',
    'author_email': 'davidmkyalo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pyuzi/uzi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
