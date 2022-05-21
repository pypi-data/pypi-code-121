# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tptp_lark_parser']

package_data = \
{'': ['*'],
 'tptp_lark_parser': ['resources/*',
                      'resources/TPTP-mock/Axioms/*',
                      'resources/TPTP-mock/Problems/TST/*']}

install_requires = \
['lark-parser']

extras_require = \
{':python_version < "3.9"': ['importlib_resources']}

setup_kwargs = {
    'name': 'tptp-lark-parser',
    'version': '0.0.2',
    'description': 'A TPTP parser using Lark',
    'long_description': '..\n  Copyright 2022 Boris Shminke\n\n  Licensed under the Apache License, Version 2.0 (the "License");\n  you may not use this file except in compliance with the License.\n  You may obtain a copy of the License at\n\n      https://www.apache.org/licenses/LICENSE-2.0\n\n  Unless required by applicable law or agreed to in writing, software\n  distributed under the License is distributed on an "AS IS" BASIS,\n  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n  See the License for the specific language governing permissions and\n  limitations under the License.\n\n|Binder|\\ |PyPI version|\\ |CircleCI|\\ |Documentation Status|\\ |codecov|\n\ntptp-lark-parser\n================\n\n``tptp-lark-parser`` is an parser for the `TPTP library\n<http://tptp.org>`__ language using the `Lark parser\n<https://github.com/lark-parser/lark>`__.\n\nHow to Install\n==============\n\nThe best way to install this package is to use ``pip``:\n\n.. code:: sh\n\n   pip install tptp-lark-parser\n   \nOne can also run it in a Docker container:\n\n.. code:: sh\n\n   docker build -t tptp-lark-parser https://github.com/inpefess/tptp-lark-parser.git\n   docker run -it --rm -p 8888:8888 tptp-lark-parser jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser\n\nHow to use\n==========\n\n.. code:: python\n\n   from tptp_lark_parser.tptp_parser import TPTPParser\n\n   tptp_parser = TPTPParser()\n   parsed_text = tptp_parser.parse("cnf(test, axiom, ~ p(Y, X) | q(X, Y)).")\n   clause_literals = parsed_text[0].literals\n   \nSee `the\nnotebook <https://github.com/inpefess/tptp-lark-parser/blob/master/examples/example.ipynb>`__\nor run it in\n`Binder <https://mybinder.org/v2/gh/inpefess/tptp-lark-parser/HEAD?labpath=example.ipynb>`__\nfor more information.\n\nHow to Contribute\n=================\n\n`Pull requests <https://github.com/inpefess/tptp-lark-parser/pulls>`__ are\nwelcome. To start:\n\n.. code:: sh\n\n   git clone https://github.com/inpefess/tptp-lark-parser\n   cd tptp-lark-parser\n   # activate python virtual environment with Python 3.7+\n   pip install -U pip\n   pip install -U setuptools wheel poetry\n   poetry install\n   # recommended but not necessary\n   pre-commit install\n\nTo check the code quality before creating a pull request, one might run\nthe script ``local-build.sh``. It locally does nearly the same as the CI\npipeline after the PR is created.\n\nReporting issues or problems with the software\n==============================================\n\nQuestions and bug reports are welcome on `the\ntracker <https://github.com/inpefess/tptp-lark-parser/issues>`__.\n\nMore documentation\n==================\n\nMore documentation can be found\n`here <https://tptp-lark-parser.readthedocs.io/en/latest>`__.\n\n.. |PyPI version| image:: https://badge.fury.io/py/tptp-lark-parser.svg\n   :target: https://badge.fury.io/py/tptp-lark-parser\n.. |CircleCI| image:: https://circleci.com/gh/inpefess/tptp-lark-parser.svg?style=svg\n   :target: https://circleci.com/gh/inpefess/tptp-lark-parser\n.. |Documentation Status| image:: https://readthedocs.org/projects/tptp-lark-parser/badge/?version=latest\n   :target: https://tptp-lark-parser.readthedocs.io/en/latest/?badge=latest\n.. |codecov| image:: https://codecov.io/gh/inpefess/tptp-lark-parser/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/inpefess/tptp-lark-parser\n.. |Binder| image:: https://mybinder.org/badge_logo.svg\n   :target: https://mybinder.org/v2/gh/inpefess/tptp-lark-parser/HEAD?labpath=example.ipynb\n',
    'author': 'Boris Shminke',
    'author_email': 'boris@shminke.ml',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inpefess/tptp-lark-parser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
