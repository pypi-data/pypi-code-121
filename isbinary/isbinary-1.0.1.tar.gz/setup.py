# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['isbinary']

package_data = \
{'': ['*']}

install_requires = \
['chardet>=3.0.2,<5.0.0']

setup_kwargs = {
    'name': 'isbinary',
    'version': '1.0.1',
    'description': 'Lightweight pure Python package to check if a file is binary or text.',
    'long_description': '========\nisbinary\n========\n\n.. image:: https://github.com/djmattyg007/python-isbinary/workflows/CI/badge.svg?branch=main\n   :target: https://github.com/djmattyg007/freiner/actions?query=branch%3Amain+workflow%3ACI\n   :alt: CI\n\n.. image:: https://codecov.io/gh/djmattyg007/python-isbinary/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/djmattyg007/python-isbinary\n   :alt: Coverage\n\n.. image:: https://img.shields.io/pypi/v/isbinary.svg\n   :target: https://pypi.org/pypi/isbinary\n   :alt: PyPI\n\n.. image:: https://img.shields.io/pypi/l/isbinary.svg\n   :target: https://pypi.org/project/isbinary\n   :alt: BSD License\n\n.. image:: https://readthedocs.org/projects/isbinary/badge/?version=latest\n   :target: https://isbinary.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n\nLightweight pure Python package to guess whether a file is binary or text,\nusing a heuristic similar to Perl\'s `pp_fttext` and its analysis by @eliben.\n\n* Free software: BSD license\n* Documentation: https://isbinary.readthedocs.io/\n\nStatus\n------\n\nIt works, and people are using this package in various places. But it doesn\'t cover all edge cases yet.\n\nThe code could be improved. Pull requests welcome! As of now, it is based on these snippets, but that may change:\n\n* https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python\n* https://stackoverflow.com/questions/1446549/how-to-identify-binary-and-text-files-using-python\n* https://code.activestate.com/recipes/173220/\n* https://eli.thegreenplace.net/2011/10/19/perls-guess-if-file-is-text-or-binary-implemented-in-python/\n\nFeatures\n--------\n\nHas tests for these file types:\n\n* Text: .txt, .css, .json, .svg, .js, .lua, .pl, .rst\n* Binary: .png, .gif, .jpg, .tiff, .bmp, .DS_Store, .eot, .otf, .ttf, .woff, .rgb\n\nHas tests for numerous encodings.\n\nWhy?\n----\n\nYou may be thinking, "I can write this in 2 lines of code?!"\n\nIt\'s actually not that easy. Here\'s a great article about how Perl\'s\nheuristic to guess file types works: https://eli.thegreenplace.net/2011/10/19/perls-guess-if-file-is-text-or-binary-implemented-in-python/\n\nAnd that\'s just where we started. Over time, we\'ve found more edge cases and\nour heuristic has gotten more complex.\n\nAlso, this package saves you from having to write and thoroughly test\nyour code with all sorts of weird file types and encodings, cross-platform.\n\nHistory\n-------\n\nThis is a long-term fork of `binaryornot <https://github.com/audreyfeldroy/binaryornot>`_. It was created in\nMay 2022 primarily because it appeared that upstream had been abandoned. There were a few other smaller issues:\n\n1. Lack of type annotations.\n2. Lack of stricter modern code quality tools used in CI.\n3. Improved contributor experience by using Github Actions for CI.\n4. Possibility for optimisation with optional dependency on `cchardet`.\n5. Removal of Python 2 support, and explicit support for newer versions of Python 3.\n\nCredits\n-------\n\n* Audrey and Danny Roy Greenfeld, as the previous maintainers of this code.\n* Special thanks to Eli Bendersky (@eliben) for his writeup explaining the heuristic and his implementation, which this is largely based on.\n* Source code from the portion of Perl\'s `pp_fttext` that checks for textiness: https://github.com/Perl/perl5/blob/v5.23.1/pp_sys.c#L3527-L3587\n',
    'author': 'Matthew Gamble',
    'author_email': 'git@matthewgamble.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/djmattyg007/python-isbinary',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
