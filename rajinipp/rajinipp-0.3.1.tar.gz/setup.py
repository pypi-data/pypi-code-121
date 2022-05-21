# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rajinipp', 'rajinipp.ast', 'rajinipp.parser']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.6.0,<0.7.0',
 'munch>=2.5.0,<3.0.0',
 'rply>=0.7.8,<0.8.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['rajinipp = rajinipp.__main__:app']}

setup_kwargs = {
    'name': 'rajinipp',
    'version': '0.3.1',
    'description': 'Rajini++ (rajiniPP) is a programming language based on the iconic dialogues by Rajinikanth.',
    'long_description': '# rajini++\n\n![banner_thin](https://user-images.githubusercontent.com/6749212/168450764-5ae486d8-8299-4425-b51d-cf3b9538efb2.png)\n\n\n\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/aadhithya/rajiniPP/Test%20and%20Release?logo=Github%20Actions&logoColor=%23fff&style=flat-square)](https://github.com/aadhithya/rajiniPP/actions/workflows/release.yml)\n[![GitHub issues](https://img.shields.io/github/issues/aadhithya/rajiniPP?style=flat-square)](https://github.com/aadhithya/rajiniPP/issues)\n[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/aadhithya/rajiniPP?logo=semantic%20release&style=flat-square)](https://pypi.org/project/rajinipp/)\n![GitHub Release Date](https://img.shields.io/github/release-date/aadhithya/rajiniPP?logo=semantic%20release&style=flat-square)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rajinipp?logo=PyPI&logoColor=%23eaeaea&style=flat-square)\n![PyPI - License](https://img.shields.io/pypi/l/rajinipp?style=flat-square)\n![GitHub commits since latest release (by SemVer)](https://img.shields.io/github/commits-since/aadhithya/rajiniPP/latest/master?style=flat-square)\n\n\n[![Twitter Follow](https://img.shields.io/twitter/follow/asankar96?style=social)](https://twitter.com/asankar96)\n[![GitHub followers](https://img.shields.io/github/followers/aadhithya?style=social)](https://github.com/aadhithya)\n\n\nrajini++ (rajiniPP) is a programming language is a tribute to the one and only superstar and based on the iconic dialogues of Rajinikanth. This is a hobby project ans is not meant to be used for serious software development.\n\n## Superstar Rajinikanth\n- [Who is Rajinikanth](https://www.youtube.com/watch?v=YDUQZwMHMoo)?\n- [Rajinikanth on Wikipedia](https://en.wikipedia.org/wiki/Rajinikanth).\n\n## Installation\n- rajinipp requires **python >= 3.8**. Install python from [here](https://www.python.org/downloads/).\n- Install the rajini++ interpreter using the following command:\n  `pip install rajinipp`\n\n- test installation: `rajinipp version`\n\n## Getting started\n\nrajini++ is not a feature rich language and is not intended for serious use. It is rather a hobby project and a tribute to the one and only superstar.\n\n### Run programs\n`hello_world.rpp`:\n```\nLAKSHMI START\nDOT "Hello, World!";\nMAGIZHCHI\n```\n- Run the `hello_world.rpp` program:\n\n  `rajinipp run examples/hello_world.rpp`\n\nwill result in the following output:\n\n![hello world output](./imgs/hello-out.png)\n\n\n\n## Resources\n- **Learn the rajini++ language**:\n  -  **The rajini++ language documentation** can be found at the [rajiniPP Wiki](https://github.com/aadhithya/rajiniPP/wiki/).\n  -  Example programs can be found here: [Example Programs](https://github.com/aadhithya/rajiniPP/tree/master/examples).\n- **The rajini++ Language Spec**: The rajini++ commands and its equivalent in python3 can be found at the [rajiniPP Language Spec](https://github.com/aadhithya/rajiniPP/wiki/rajiniPP:-Language-Specification) wiki.\n- **The rajinipp Interpreter Documentation**: The documentation for the rajinipp interpreter can be found [here](https://github.com/aadhithya/rajiniPP/wiki/rajinipp:-The-interpreter).\n\n\n## Acknowledgements\n- A lot of learnings from [DIVSPL](https://github.com/di/divspl) and its accompanying [pycon talk](https://www.youtube.com/watch?v=ApgUrtCrmV8).\n- A lot of learnings from [this pycon talk](https://www.youtube.com/watch?v=LCslqgM48D4&t=1388s) by [Alex Gaynor](alex).\n- Workflows setup based on [poetry_pypi_template](https://github.com/a-parida12/poetry_pypi_template).\n- This project is inspired by the [ArnoldC](https://github.com/lhartikk/ArnoldC) project.\n\n\n\n## Roadmap\n### rajini++ Features\n- [x] Math Ops\n  - [x] SUM\n  - [x] SUB\n  - [x] MUL\n  - [x] DIV\n  - [x] MOD\n- [x] Unary Ops\n- [x] print multiple objects with the same statement.\n- [x] variable declaration\n- [x] variable access\n- [x] variable manipulation\n- [x] bool data type\n- [x] float datatype\n- [x] logical ops\n- [x] if statement\n- [x] if-else statement\n- [x] for loop\n- [x] while loop\n- [x] functions\n- [x] functions with return\n- [ ] fuinctions with arguments\n- [ ] Execute python code in rajini++ scripts\n### rajinipp package\n- [ ] rajinipp python runner:\n  - [ ] `rajinipp.api.require`: load rajini++ code into python program.\n  - [x] `rajinipp.runner.RppRunner.exec`: execute rajini++ programs in python loaded as string.\n  - [ ] `rajinipp.runner.RppRunner.eval`:\n    - [x] eval rajini++ statement in python scripts [limited support].\n    - [ ] support flow control statements.\n    - [ ] eval function calls from loaded rajini++ code and return output.\n- [ ] rajinipp shell to run rajini++ commands from the terminal.\n  - [x] limited support using `rajinipp.runner.RppRunner.eval`.\n  - [ ] complete support to all rajini++ features.\n\n### General\n- [x] Add tests.\n- [x] semantic releases.\n',
    'author': 'Aadhithya Sankar',
    'author_email': 'a.sankar@tum.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aadhithya/rajiniPP',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
