# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modelator_py',
 'modelator_py.apalache',
 'modelator_py.tlc',
 'modelator_py.util',
 'modelator_py.util.tla',
 'modelator_py.util.tla.examples',
 'modelator_py.util.tlc']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.4.0,<0.5.0',
 'infix==1.2',
 'pathos>=0.2.8,<0.3.0',
 'ply==3.10',
 'recordclass>=0.16.2,<0.17.0']

entry_points = \
{'console_scripts': ['modelator = modelator_py.cli:cli']}

setup_kwargs = {
    'name': 'modelator-py',
    'version': '0.1.9',
    'description': 'Lightweight utilities to assist model writing and model-based testing activities using the TLA+ ecosystem',
    'long_description': '# modelator-py\n\n|⚠️ The tools in this repo are unstable and may be subject to major changes ⚠️|\n|-|\n\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)\n[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)\n[![PyPI](https://img.shields.io/pypi/v/modelator-py?label=pypi%20package)](https://pypi.python.org/pypi/modelator-py/)\n[![Downloads](https://pepy.tech/badge/modelator-py/month)](https://pepy.tech/project/modelator-py)\n\n_**Lightweight utilities to assist model writing and model-based testing activities using the TLA+ ecosystem.**_\n\n## What is this project?\n\nA collection of cli utilities and library functions to reduce leg-work when developing TLA+ models, running model checkers, and doing model-based testing. The utilities are also intended to act as building blocks for tool development in the TLA+ ecosystem.\n\n### What can it do right now?\n\nCurrently there is a cli and library functions implementing utilities:\n\n- [x] Run [TLC](https://github.com/tlaplus/tlaplus) model checker without side effects (runs in temporary directory and is cleaned up)\n- [x] Run [TLC](https://github.com/tlaplus/tlaplus) model checker programmatically (reads and returns json data)\n- [x] Run [Apalache](https://github.com/informalsystems/apalache) model checker without side effects (runs in temporary directory and is cleaned up)\n- [x] Run [Apalache](https://github.com/informalsystems/apalache) model checker programmatically (reads and returns json data)\n- [x] Extract traces from TLC output in [Informal Trace Format](https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#the-itf-format) format (concise and machine readable counterexample representation)\n\nAllowing clean programmatic access to model checkers and other utility.\n\n### What will it do in the future?\n\nThe model-based testing capabilities developed at Informal are currently in the [modelator](https://github.com/informalsystems/modelator) tool and are being migrated to a multi language architecture. Please expect more utilities and more tooling soon.\n\n## Usage\n\nPlease see [usage](./samples/usage.md).\n\n## Running the code in this repository\n\nPlease see [contributing](./CONTRIBUTING.md).\n\n## Contributing\n\nPlease see [contributing](./CONTRIBUTING.md).\n\n## License\n\nCopyright © 2021 Informal Systems Inc. and modelator authors.\n\nLicensed under the Apache License, Version 2.0 (the "License"); you may not use the files in this repository except in compliance with the License. You may obtain a copy of the License at\n\n    https://www.apache.org/licenses/LICENSE-2.0\n',
    'author': 'Daniel Tisdall',
    'author_email': 'daniel@informal.systems',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://mbt.informal.systems/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9.7,<4.0.0',
}


setup(**setup_kwargs)
