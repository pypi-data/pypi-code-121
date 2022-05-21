# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybtexnbib']

package_data = \
{'': ['*'], 'pybtexnbib': ['data/*']}

install_requires = \
['pybtex>=0.24.0,<0.25.0', 'pybtexris>=0.1.1,<0.2.0']

entry_points = \
{'pybtex.database.input': ['nbib = pybtexnbib:NBIBParser'],
 'pybtex.database.input.suffixes': ['.nbib = pybtexnbib:NBIBParser']}

setup_kwargs = {
    'name': 'pybtexnbib',
    'version': '0.1.1',
    'description': 'A pybtex plugin for NBIB/Medline/PubMed files',
    'long_description': '============\npybtexnbib\n============\n\n.. start-badges\n\n|pipline badge| |coverage badge| |black badge| |git3moji badge|\n\n.. |pipline badge| image:: https://github.com/rbturnbull/pybtexnbib/actions/workflows/coverage.yml/badge.svg\n    :target: https://github.com/rbturnbull/pybtexnbib/actions\n    \n.. |coverage badge| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/e93cbe3d6bef10cf72db901d962719ba/raw/coverage-badge.json\n    :target: https://rbturnbull.github.io/pybtexnbib/\n\n.. |black badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    \n.. |git3moji badge| image:: https://img.shields.io/badge/git3moji-%E2%9A%A1%EF%B8%8F%F0%9F%90%9B%F0%9F%93%BA%F0%9F%91%AE%F0%9F%94%A4-fffad8.svg\n    :target: https://robinpokorny.github.io/git3moji/\n\n.. end-badges\n\nA pybtex plugin for NBIB/Medline/PubMed files. For information on the file format, see the documentation at the `National Library of Medicine <https://www.nlm.nih.gov/bsd/mms/medlineelements.html>`_.\n\nInstallation\n============\n\nInstall pybtexnbib from PyPI using pip::\n\n    pip install pybtexnbib\n\nCommand-line usage\n==================\n\nTo convert an NBIB file to another format, use the ``pybtex-convert`` command. For example::\n\n    pybtex-convert bibliography.nbib bibliography.bib\n\nThe extension of the output file must be supported by ``pybtex`` or an associated plugin.\n\nTo format an NBIB file into a human-readable bibliography, use the pybtex-format command. For example::\n\n    pybtex-format bibliography.nbib bibliography.txt\n\nFor more information, see `the documentation for pybtex <https://docs.pybtex.org/cmdline.html>`_.\n\nProgrammatic usage\n==================\n\nNBIB files can be formatted into a human-readable bibliography as a string as follows:\n\n.. code-block:: python\n\n    from pybtex import format_from_file\n    bibliography_string = format_from_file(\n        "path/to/file.nbib", \n        style="plain", \n        output_backend="plaintext",\n        bib_format="nbib",\n    )\n\nMultiple NBIB files can be formatted in a similar way:\n\n.. code-block:: python\n\n    from pybtex import format_from_files\n    bibliography_string = format_from_files(\n        ["path/to/file1.nbib", "path/to/file2.nbib"],\n        style="plain", \n        output_backend="plaintext",\n        bib_format="nbib",\n    )\n\nBy giving ``"suffix"`` as the argument to ``bib_format``, \nNBIB files can be combined with bibliography files of other formats (such as BibTeX or RIS):\n\n.. code-block:: python\n\n    from pybtex import format_from_files\n    bibliography_string = format_from_files(\n        ["path/to/file1.nbib", "path/to/file2.bib", "path/to/file3.ris"],\n        style="plain", \n        output_backend="plaintext",\n        bib_format="suffix",\n    )\n\nThe RIS parser comes from `pybtexris <https://github.com/rbturnbull/pybtexris>`_. \nParsers for the files for other formats need to be registered on the ``pybtex.database.input.suffixes``\nentry point as discussed pybtex `plugin documentation <https://docs.pybtex.org/api/plugins.html>`_.\n\nFor more information on programmatic use of pybtex, \nsee `the documentation of the Python API of pybtex <https://docs.pybtex.org/api/index.html>`_.\n\nCredit\n==================\n\nRobert Turnbull (Melbourne Data Analytics Platform, University of Melbourne)\n',
    'author': 'Robert Turnbull',
    'author_email': 'robert.turnbull@unimelb.edu.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rbturnbull/pybtexnbib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
