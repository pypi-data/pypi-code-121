# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybtexris']

package_data = \
{'': ['*'], 'pybtexris': ['data/*']}

install_requires = \
['pybtex>=0.24.0,<0.25.0']

entry_points = \
{'pybtex.database.input': ['ris = pybtexris:RISParser',
                           'suffix = pybtexris:SuffixParser'],
 'pybtex.database.input.suffixes': ['.ris = pybtexris:RISParser']}

setup_kwargs = {
    'name': 'pybtexris',
    'version': '0.1.1',
    'description': 'A pybtex plugin for working with RIS files.',
    'long_description': '============\npybtexris\n============\n\n.. start-badges\n\n|pipline badge| |coverage badge| |black badge| |git3moji badge|\n\n.. |pipline badge| image:: https://github.com/rbturnbull/pybtexris/actions/workflows/coverage.yml/badge.svg\n    :target: https://github.com/rbturnbull/pybtexris/actions\n    \n.. |black badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    \n.. |coverage badge| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/665c8745fce7077155f99ad694a7e762/raw/coverage-badge.json\n    :target: https://rbturnbull.github.io/pybtexris/\n\n.. |git3moji badge| image:: https://img.shields.io/badge/git3moji-%E2%9A%A1%EF%B8%8F%F0%9F%90%9B%F0%9F%93%BA%F0%9F%91%AE%F0%9F%94%A4-fffad8.svg\n    :target: https://robinpokorny.github.io/git3moji/\n\n.. end-badges\n\nA pybtex plugin for working with RIS files.\n\nInstallation\n============\n\nInstall pybtexris from PyPI using pip::\n\n    pip install pybtexris\n\nCommand-line usage\n==================\n\nTo convert an RIS file to another format, use the ``pybtex-convert`` command. For example::\n\n    pybtex-convert bibliography.ris bibliography.bib\n\nThe extension of the output file must be supported by ``pybtex`` or an associated plugin.\n\nTo format an RIS file into a human-readable bibliography, use the pybtex-format command. For example::\n\n    pybtex-format bibliography.ris bibliography.txt\n\nFor more information, see `the documentation for pybtex <https://docs.pybtex.org/cmdline.html>`_.\n\nProgrammatic usage\n==================\n\nRIS files can be formatted into a human-readable bibliography as a string as follows:\n\n.. code-block:: python\n\n    from pybtex import format_from_file\n    bibliography_string = format_from_file(\n        "path/to/file.ris", \n        style="plain", \n        output_backend="plaintext",\n        bib_format="ris",\n    )\n\nMultiple RIS files can be formatted in a similar way:\n\n.. code-block:: python\n\n    from pybtex import format_from_files\n    bibliography_string = format_from_files(\n        ["path/to/file1.ris", "path/to/file2.ris"],\n        style="plain", \n        output_backend="plaintext",\n        bib_format="ris",\n    )\n\nSo that RIS files can be combined with bibliography files of other formats (such as BibTeX), \n`pybtexris` also adds `SuffixParser` to the list of plugins which pybtex can use.\nThe user just needs to give ``suffix`` as the argument to ``bib_format``.\n\n.. code-block:: python\n\n    from pybtex import format_from_files\n    result = format_from_files(\n        ["path/to/file1.ris", "path/to/file2.bib"],\n        style="plain", \n        output_backend="plaintext",\n        bib_format="suffix",\n    )\n\nThe parsers for the files for other formats need to be registered on the ``pybtex.database.input.suffixes``\nentry point as discussed pybtex `plugin documentation <https://docs.pybtex.org/api/plugins.html>`_.\nTo combine with NBIB citation files, please use the `pybtexnbib <https://github.com/rbturnbull/pybtexnbib>`_ plugin.\n\nFor more information on programmatic use of pybtex, \nsee `the documentation of the Python API of pybtex <https://docs.pybtex.org/api/index.html>`_.\n\nCredit\n==================\n\nRobert Turnbull (Melbourne Data Analytics Platform, University of Melbourne)',
    'author': 'Robert Turnbull',
    'author_email': 'robert.turnbull@unimelb.edu.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rbturnbull/pybtexris',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
