# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pynguin',
 'pynguin.analyses',
 'pynguin.assertion',
 'pynguin.assertion.mutation_analysis',
 'pynguin.coverage',
 'pynguin.ga',
 'pynguin.ga.comparators',
 'pynguin.ga.operators',
 'pynguin.ga.operators.crossover',
 'pynguin.ga.operators.ranking',
 'pynguin.ga.operators.selection',
 'pynguin.generation',
 'pynguin.generation.algorithms',
 'pynguin.generation.stoppingconditions',
 'pynguin.instrumentation',
 'pynguin.resources',
 'pynguin.testcase',
 'pynguin.utils',
 'pynguin.utils.generic',
 'pynguin.utils.statistics']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1,<4.0',
 'MutPy-Pynguin>=0.7.1,<0.8.0',
 'Pygments>=2.12,<3.0',
 'bytecode>=0,<1',
 'jellyfish>=0,<1',
 'networkx>=2.8,<3.0',
 'ordered-set>=4.1,<5.0',
 'pydot>=1.4,<2.0',
 'pytest>=7.1,<8.0',
 'rich>=12.4,<13.0',
 'simple-parsing>=0.0.19,<0.0.20',
 'typing_inspect>=0,<1']

entry_points = \
{'console_scripts': ['pynguin = pynguin.cli:main']}

setup_kwargs = {
    'name': 'pynguin',
    'version': '0.20.1',
    'description': 'Pynguin is a tool for automated unit test generation for Python',
    'long_description': '<!--\nSPDX-FileCopyrightText: 2019–2022 Pynguin Contributors\n\nSPDX-License-Identifier: CC-BY-4.0\n-->\n\n# Pynguin\n\nPynguin (IPA: ˈpɪŋɡuiːn),\nthe\nPYthoN\nGeneral\nUnIt\ntest\ngeNerator,\nis a tool that allows developers to generate unit tests automatically.\n\nTesting software is often considered to be a tedious task.\nThus, automated generation techniques have been proposed and mature tools exist—for\nstatically typed languages, such as Java.\nThere is, however, no fully-automated tool available that produces unit tests for\ngeneral-purpose programs in a dynamically typed language.\nPynguin is, to the best of our knowledge, the first tool that fills this gap\nand allows the automated generation of unit tests for Python programs.\n\nPynguin is developed at the\n[Chair of Software Engineering II](https://www.fim.uni-passau.de/lehrstuhl-fuer-software-engineering-ii/) \nof the [University of Passau](https://www.uni-passau.de).\n\n<details>\n<summary>Internal Pipeline Status</summary>\n\n[![pipeline status](https://gitlab.infosun.fim.uni-passau.de/se2/pynguin/pynguin/badges/main/pipeline.svg)](https://gitlab.infosun.fim.uni-passau.de/se2/pynguin/pynguin/-/commits/main)\n[![coverage report](https://gitlab.infosun.fim.uni-passau.de/se2/pynguin/pynguin/badges/main/coverage.svg)](https://gitlab.infosun.fim.uni-passau.de/se2/pynguin/pynguin/-/commits/main)  \n\n</details>\n\n[![License LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![PyPI version](https://badge.fury.io/py/pynguin.svg)](https://badge.fury.io/py/pynguin)\n[![Supported Python Versions](https://img.shields.io/pypi/pyversions/pynguin.svg)](https://github.com/se2p/pynguin)\n[![Documentation Status](https://readthedocs.org/projects/pynguin/badge/?version=latest)](https://pynguin.readthedocs.io/en/latest/?badge=latest)\n[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3989840.svg)](https://doi.org/10.5281/zenodo.3989840)\n[![REUSE status](https://api.reuse.software/badge/github.com/se2p/pynguin)](https://api.reuse.software/info/github.com/se2p/pynguin)\n[![Downloads](https://static.pepy.tech/personalized-badge/pynguin?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/pynguin)\n\n\n![Pynguin Logo](https://raw.githubusercontent.com/se2p/pynguin/master/docs/source/_static/pynguin-logo.png "Pynguin Logo")\n\n## Attention\n\nPynguin executes the module under test!\nAs a consequence, depending on what code is in that module,\nrunning Pynguin can cause serious harm to your computer,\nfor example, wipe your entire hard disk!\nWe recommend running Pynguin in an isolated environment;\nuse, for example, a Docker container to minimize the risk of damaging\nyour system.\n\n\n## Prerequisites\n\nBefore you begin, ensure you have met the following requirements:\n- You have installed Python 3.10 (we have not yet tested with Python\n  3.11, there might be some problems due to changed internals regarding the byte-code\n  instrumentation).\n\n  **Attention:** Pynguin now requires Python 3.10!  Older versions are no longer \n  supported!\n- You have a recent Linux/macOS/Windows machine.\n\nPlease consider reading the [online documentation](https://pynguin.readthedocs.io)\nto start your Pynguin adventure.\n \n## Installing Pynguin\n\nPynguin can be easily installed using the `pip` tool by typing:\n```bash\npip install pynguin\n```\n\nMake sure that your version of `pip` is that of a supported Python version, as any \nolder version is not supported by Pynguin!\n\n## Using Pynguin\n\nBefore you continue, please read the [quick start guide](https://pynguin.readthedocs.io/en/latest/user/quickstart.html)\n\nPynguin is a command-line application.\nOnce you installed it to a virtual environment, you can invoke the tool by typing\n`pynguin` inside this virtual environment.\nPynguin will then print a list of its command-line parameters.\n\nA minimal full command line to invoke Pynguin could be the following,\nwhere we assume that a project `foo` is located in `/tmp/foo`,\nwe want to store Pynguin\'s generated tests in `/tmp/testgen`,\nand we want to generate tests using a whole-suite approach for the module `foo.bar`\n(wrapped for better readability):\n```bash\npynguin \\\n  --project-path /tmp/foo \\\n  --output-path /tmp/testgen \\\n  --module-name foo.bar\n```\nPlease find a more detailed example in the [quick start guide](https://pynguin.readthedocs.io/en/latest/user/quickstart.html).\n\n\n## Contributing to Pynguin\n\nFor the development of Pynguin you will need the [`poetry`](https://python-poetry.org)\ndependency management and packaging tool.\nTo start developing, follow these steps:\n1. Clone the repository\n2. Change to the `pynguin` folder: `cd pynguin`\n3. Create a virtual environment and install dependencies using `poetry`: `poetry install`\n4. Make your changes\n5. Run `poetry shell` to switch to the virtual environment in your current shell\n6. Run `make check` to verify that your changes pass all checks\n\n   Please see the [`poetry` documentation](https://python-poetry.org/docs/) for more information on this tool.\n\n### Development using PyCharm.\n\nIf you want to use the PyCharm IDE you have to set up a few things:\n1. Import pynguin into PyCharm.\n2. Let the poetry support configure a virtual environment.\n\n   If you use a PyCharm version before `2021.3`, you have to install the poetry support as a [plugin](https://plugins.jetbrains.com/plugin/14307-poetry).\n3. Set the default test runner to `pytest`\n4. Set the DocString format to `Google`\n\n\n## License\n\nThis project is licensed under the terms of the\n[GNU Lesser General Public License](LICENSE.rst).\n',
    'author': 'Stephan Lukasczyk',
    'author_email': 'stephan@lukasczyk.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.pynguin.eu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
