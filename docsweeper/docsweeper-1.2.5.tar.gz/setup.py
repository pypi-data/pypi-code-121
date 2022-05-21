# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['_docsweeper', 'docsweeper', 'flake8_plugin']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.0,<9.0.0']

entry_points = \
{'console_scripts': ['docsweeper = _docsweeper.command_line:parse_args'],
 'flake8.extension': ['DOC100 = flake8_plugin.Plugin:Plugin']}

setup_kwargs = {
    'name': 'docsweeper',
    'version': '1.2.5',
    'description': 'A linter for your Python code base that finds potentially outdated docstrings using version control.',
    'long_description': '============\n Docsweeper\n============\n\n.. image:: https://img.shields.io/pypi/pyversions/docsweeper?style=flat-square\n   :alt: PyPI - Python Version\n   :target: https://pypi.org/project/docsweeper/\n\n.. image:: https://img.shields.io/pypi/v/docsweeper?style=flat-square\n   :alt: PyPI\n   :target: https://pypi.org/project/docsweeper/\n\n.. image:: https://img.shields.io/pypi/l/docsweeper?style=flat-square\n   :alt: PyPI - License\n   :target: https://pypi.org/project/docsweeper/\n\n.. image:: https://readthedocs.org/projects/docsweeper/badge/?version=stable&style=flat-square\n   :target: https://docsweeper.readthedocs.io/en/stable/?badge=stable\n   :alt: Documentation Status\n\n.. image:: https://img.shields.io/travis/com/thueringa/docsweeper?style=flat-square\n   :alt: Travis (.com)\n   :target: https://app.travis-ci.com/github/thueringa/docsweeper\n\n.. image:: https://img.shields.io/appveyor/build/AndreasThring/docsweeper\n   :alt: AppVeyor\n   :target: https://ci.appveyor.com/project/AndreasThring/docsweeper\n\n*Docsweeper* is a linter for version controlled *Python* code bases that finds\npotentially outdated docstrings in your source files. For every code token in the file\nthat has a docstring (see `PEP 257 <https://peps.python.org/pep-0257/>`_), *Docsweeper*\nwill interact with your *Git* or *Mercurial* version control system to determine:\n\n#. in which revision the docstring has last been changed, and\n#. how often the source code that is referenced by the docstring has been altered since\n   that revision.\n\nUsed as a stand-alone application or as a plugin for the `Flake8\n<https://flake8.pycqa.org/en/latest/>`_ linter, *Docsweeper* can be integrated into your\ncode check-in or linting process easily and help you quickly determine which docstrings\npotentially contain obsolete information.\n\nCompatibility\n=============\n\n*Docsweeper* supports Linux, Mac, and Windows platforms that are compatible with Python\n3.7 or newer. In addition to a working Python installation, you will also need at least\none of the version control systems you intend to use *Docsweeper* with:\n\n#. `Git <https://git-scm.com/>`_ v1.7.0 or newer, and/or\n#. `Mercurial <https://www.mercurial-scm.org/>`_ v5.2 or newer. This is the the first\n   release of *Mercurial* with `official support\n   <https://www.mercurial-scm.org/wiki/Python3>`_ for *Python* 3.\n\n\nRefer to the `documentation <https://docsweeper.readthedocs.io/>`_ for more information.\n',
    'author': 'Andreas Thüring',
    'author_email': 'a.thuering@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://docsweeper.readthedocs.io/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
