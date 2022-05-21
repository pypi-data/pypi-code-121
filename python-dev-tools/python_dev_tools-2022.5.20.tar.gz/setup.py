# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_dev_tools', 'python_dev_tools.formatters']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx>=4,<5',
 'autoflake>=1,<2',
 'bandit==1.7.2',
 'black>=22,<23',
 'cohesion>=1,<2',
 'coverage>=6,<7',
 'darglint>=1,<2',
 'dlint>=0,<1',
 'doc8>=0,<1',
 'flake8-2020>=1,<2',
 'flake8-annotations-complexity>=0,<1',
 'flake8-annotations-coverage>=0,<1',
 'flake8-annotations>=2,<3',
 'flake8-bandit>=2,<3',
 'flake8-black>=0,<1',
 'flake8-broken-line>=0,<1',
 'flake8-bugbear>=21,<22',
 'flake8-builtins>=1,<2',
 'flake8-comprehensions>=3,<4',
 'flake8-debugger>=4,<5',
 'flake8-docstrings>=1,<2',
 'flake8-eradicate>=1,<2',
 'flake8-expression-complexity>=0,<1',
 'flake8-fixme>=1,<2',
 'flake8-functions>=0,<1',
 'flake8-isort>=4,<5',
 'flake8-logging-format>=0,<1',
 'flake8-mutable>=1,<2',
 'flake8-pytest-style>=1,<2',
 'flake8-quotes>=3,<4',
 'flake8-rst-docstrings>=0,<1',
 'flake8-simplify>=0,<1',
 'flake8-string-format>=0,<1',
 'flake8-tidy-imports>=4,<5',
 'flake8-typing-imports>=1,<2',
 'flake8-use-fstring>=1,<2',
 'flake8-variables-names>=0,<1',
 'flake8>=4,<5',
 'pep8-naming>=0,<1',
 'pip>=22,<23',
 'pycodestyle>=2,<3',
 'pydocstyle>=6,<7',
 'pyflakes>=2,<3',
 'pytest-cov>=3,<4',
 'pytest-sugar>=0,<1',
 'pytest>=7,<8',
 'pyupgrade>=2,<3',
 'tox-travis>=0,<1',
 'tox>=3,<4',
 'wemake-python-styleguide>=0.16,<0.17']

entry_points = \
{'console_scripts': ['whataformatter = python_dev_tools.whataformatter:main'],
 'flake8.extension': ['WAL = python_dev_tools.whatalinter:WhatALinter']}

setup_kwargs = {
    'name': 'python-dev-tools',
    'version': '2022.5.20',
    'description': 'Needed and up-to-date tools to develop in Python',
    'long_description': 'Python Dev Tools\n================\n\nNeeded and up-to-date tools to develop in Python (*WORK IN PROGRESS*)\n\n\n.. image:: https://img.shields.io/pypi/v/python_dev_tools.svg\n        :target: https://pypi.python.org/pypi/python_dev_tools\n\n.. image:: https://img.shields.io/pypi/l/python_dev_tools.svg\n        :target: https://github.com/vpoulailleau/python_dev_tools/blob/master/LICENSE\n\n.. image:: https://travis-ci.com/vpoulailleau/python-dev-tools.svg?branch=master\n        :target: https://travis-ci.com/vpoulailleau/python-dev-tools\n\n.. image:: https://readthedocs.org/projects/python-dev-tools/badge/?version=latest\n        :target: https://python-dev-tools.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\n.. image:: https://pepy.tech/badge/python-dev-tools\n        :target: https://pepy.tech/project/python-dev-tools\n        :alt: Downloads\n\n.. image:: https://api.codeclimate.com/v1/badges/282fcd71714dabd6a847/test_coverage\n        :target: https://codeclimate.com/github/vpoulailleau/python-dev-tools/test_coverage\n        :alt: Test Coverage\n\n.. image:: https://api.codeclimate.com/v1/badges/282fcd71714dabd6a847/maintainability\n        :target: https://codeclimate.com/github/vpoulailleau/python-dev-tools/maintainability\n        :alt: Maintainability\n\n.. image:: https://bettercodehub.com/edge/badge/vpoulailleau/python-dev-tools?branch=master\n        :target: https://bettercodehub.com/results/vpoulailleau/python-dev-tools\n        :alt: Maintainability\n\n.. image:: https://img.shields.io/lgtm/grade/python/g/vpoulailleau/python-dev-tools.svg?logo=lgtm&logoWidth=1\n        :target: https://lgtm.com/projects/g/vpoulailleau/python-dev-tools/context:python\n        :alt: Maintainability\n\nSupported Python versions: the same as the classic Python interpreter (CPython)\n\nDocumentation\n-------------\n\nThe full documentation can be read at https://python-dev-tools.readthedocs.io.\n\nInstallation\n------------\n\nIn a terminal, run:\n\n.. code-block:: console\n\n    $ python3 -m pip install python-dev-tools --user --upgrade\n\nFull documentation on installation: https://python-dev-tools.readthedocs.io/en/latest/installation.html\n\nThat\'s it! Use the provided linter (``flake8``), formatter (``whataformatter``) and\nprecommit hook (TODO) where applicable.\n\nInstallation with Visual Studio Code\n------------------------------------\n\n* Follow the installation procedure for python-dev-tools\n* Be sure to have the official Python extension installed in VS Code\n* Open VS Code from within your activated virtual environment (in fact, make sure that \n  ``flake8`` from python-dev-tools is in your ``PYTHON_PATH``)\n* In VS Code, open settings (F1 key, then type "Open Settings (JSON)",\n  then enter)\n* Add in the opened JSON file (before the closing ``}``):\n\n.. code:: javascript\n\n    "python.linting.enabled": true,\n    "python.linting.flake8Enabled": true,\n    "python.linting.flake8Path": "flake8",\n    "python.formatting.provider": "black",\n    "python.formatting.blackPath": "whataformatter",\n    "python.formatting.blackArgs": [],\n\nFeatures\n--------\n\nIntegrate features of commonly used tools. This package provides usual\ndependencies to develop Python software.\n\n* Simple linter\n\n  * ``flake8 a_python_file.py`` lints a_python_file.py\n  * based on flake8 and plugins: https://gitlab.com/pycqa/flake8\n\n    * cohesion: https://github.com/mschwager/cohesion\n    * darglint: https://github.com/terrencepreilly/darglint\n    * dlint: https://github.com/dlint-py/dlint\n    * flake8-2020: https://github.com/asottile/flake8-2020\n    * flake8-annotations: https://github.com/sco1/flake8-annotations\n    * flake8-annotations-complexity:\xa0https://github.com/best-doctor/flake8-annotations-complexity\n    * flake8-annotations-coverage: https://github.com/best-doctor/flake8-annotations-coverage\n    * flake8-bandit: https://github.com/tylerwince/flake8-bandit\n    * flake8-broken-line: https://github.com/sobolevn/flake8-broken-line\n    * flake8-bugbear: https://github.com/PyCQA/flake8-bugbear\n    * flake8-builtins: https://github.com/gforcada/flake8-builtins\n    * flake8-comprehensions: https://github.com/adamchainz/flake8-comprehensions\n    * flake8-debugger: https://github.com/JBKahn/flake8-debugger\n    * flake8-docstrings: https://gitlab.com/pycqa/flake8-docstrings\n    * flake8-eradicate: https://github.com/sobolevn/flake8-eradicate\n    * flake8-expression-complexity: https://pypi.org/project/flake8-expression-complexity/\n    * flake8-fixme: https://github.com/tommilligan/flake8-fixme\n    * flake8-functions: https://github.com/best-doctor/flake8-functions\n    * flake8-isort: https://github.com/gforcada/flake8-isort\n    * flake8-logging-format: https://github.com/globality-corp/flake8-logging-format\n    * flake8-mutable: https://github.com/ebeweber/flake8-mutable\n    * flake8-pytest-style: https://github.com/m-burst/flake8-pytest-style\n    * flake8-quotes: https://github.com/zheller/flake8-quotes/\n    * flake8-rst-docstrings: https://github.com/peterjc/flake8-rst-docstrings\n    * flake8-simplify: https://github.com/MartinThoma/flake8-simplify\n    * flake8-string-format: https://github.com/xZise/flake8-string-format\n    * flake8-tidy-imports: https://github.com/adamchainz/flake8-tidy-imports\n    * flake8-typing-imports: https://github.com/asottile/flake8-typing-imports\n    * flake8-use-fstring: https://github.com/MichaelKim0407/flake8-use-fstring\n    * flake8-variables-names: https://github.com/best-doctor/flake8-variables-names\n    * pep8-naming: https://github.com/PyCQA/pep8-naming\n    * wemake-python-styleguide: https://github.com/wemake-services/wemake-python-styleguide\n\n* Simple formatter\n\n  * ``whataformatter a_python_file.py`` formats a_python_file.py\n  * based on\n\n    * autoflake: https://github.com/myint/autoflake\n    * black: https://github.com/python/black\n    * pyupgrade: https://github.com/asottile/pyupgrade\n\n* Simple precommit hook\n\n  * TODO\n\nLicense\n-------\n\nBSD 3-Clause license, feel free to contribute: https://python-dev-tools.readthedocs.io/en/latest/contributing.html.\n\nTODO\n----\n\n* documentation\n* precommit\n\nChangelog\n---------\n\n2022.5.20\n^^^^^^^^^\n\n* Add ``cohesion`` linter\n* Add ``dlint`` linter\n* Add ``flake8-annotations`` linter\n* Add ``flake8-annotations-complexity`` linter\n* Add ``flake8-annotations-coverage`` linter\n* Add ``flake8-black`` linter\n* Add ``flake8-expression-complexity`` linter\n* Add ``flake8-functions`` linter\n* Add ``flake8-pytest-style`` linter\n* Add ``flake8-simplify`` linter\n* Add ``flake8-tidy-imports`` linter\n* Add ``flake8-typing-imports`` linter\n* Add ``flake8-use-fstring`` linter\n* Remove ``flake8-commas`` linter that is deprecated\n* Fix ``whataformatter`` and add ``--target-version`` option for VS Code compatibility\n\n2020.9.10\n^^^^^^^^^\n\n* The path provided to ``whatalinter`` can be the one of a directory\n  (recursive search of Python files)\n\n2020.9.7\n^^^^^^^^\n\n* Remove E203 in ``flake8`` for ``black`` compatibility\n\n2020.9.4\n^^^^^^^^\n\n* Add ``whatalinter_vscode`` for Visual Studio Code integration\n\n2020.9.2\n^^^^^^^^\n\n* Remove some warnings of ``wemake-python-styleguide``, for instance allow f-strings\n\n2020.9.1\n^^^^^^^^\n\n* Use ``poetry``\n* Remove redundant linters\n* Change max line length to 88 (default value of ``black``)\n* Replace ``pydocstyle`` with ``flake8-docstrings``\n* Add ``wemake-python-styleguide``\n\n2019.10.22\n^^^^^^^^^^\n\n* Add ``flake8-2020`` linter\n\n2019.07.21\n^^^^^^^^^^\n\n* Add ``--quiet`` and ``--diff`` flags to ``whataformatter`` for VS Code compatibility\n\n2019.07.20\n^^^^^^^^^^\n\n* Add ``black`` formatter\n* Add ``autoflake`` formatter\n* Add ``pyupgrade`` formatter\n\n2019.04.08\n^^^^^^^^^^\n\n* Add ``flake8`` linter\n* Add ``flake8-isort`` linter\n* Add ``pep8-naming`` linter\n* Add ``flake8-comprehensions`` linter\n* Add ``flake8-logging-format`` linter\n* Add ``flake8-bugbear`` linter\n* Add ``flake8-builtins`` linter\n* Add ``flake8-broken-line`` linter\n* Add ``flake8-fixme`` linter\n* Add ``flake8-mutable`` linter\n* Add ``flake8-debugger`` linter\n* Add ``flake8-variables-names`` linter\n* Add ``flake8-bandit`` linter\n\n2019.03.02\n^^^^^^^^^^\n\n* Add ``pydocstyle`` linter\n\n2019.03.01\n^^^^^^^^^^\n\n* Add McCabe complexity checker\n\n2019.02.26\n^^^^^^^^^^\n\n* Add ``pyflakes`` linter\n* Add ``pycodestyle`` linter\n\n2019.02.23\n^^^^^^^^^^\n\n* First release on PyPI.\n',
    'author': 'Vincent Poulailleau',
    'author_email': 'vpoulailleau@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vpoulailleau/python-dev-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
