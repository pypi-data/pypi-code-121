# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['conhead']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1,<9.0', 'tomli>=2.0,<3.0']

entry_points = \
{'console_scripts': ['conhead = conhead.main:main']}

setup_kwargs = {
    'name': 'conhead',
    'version': '0.1.1',
    'description': 'Python-based tool for keeping source file headers consistent.',
    'long_description': 'Conhead\n=======\n\nConsistent header management.\n\nCLI tool for applying and maintaining consistent headers across source\nfiles.\n\n-   Add headers to files that don\'t have them.\n-   Update fields in files that already have them.\n-   Maintain different header configurations for different file\n    types\n\nInstallation\n------------\n\nConhead is available as the Python ``conhead`` package.\n\nFor example, to install using `pipx`_:\n\n.. code-block:: shell\n\n    $ pipx install conhead\n    $ conhead --help\n    Usage: conhead [OPTIONS] SRC\n\n.. _pipx: https://github.com/pypa/pipx\n\nConfiguration\n-------------\n\nConfigure ``conhead`` via `pyproject.toml`. Each header template\nis configured via a separate ``[tools.conhead.header.<name>]``\nsection. Each section is a header definition and can be applied\nto one or more file extensions.\n\n\nExample:\n\n.. code-block:: toml\n\n    [tools.conhead.header.hashhead]\n    extensions = [\'py\', \'toml\', \'yaml\']\n    template = """\n        # Copyright {{YEAR}} Organized Organization\n        # SPDX-License-Identifier: Apache-2.0\n\n    """\n\n    [tools.conhead.header.slashhead]\n    extensions = [\'c\', \'cpp\', \'java\']\n    template = """\n        // Copyright {{YEAR}} Organized Organization\n        // SPDX-License-Identifier: Apache-2.0\n\n    """\n\nTemplate Definition\n~~~~~~~~~~~~~~~~~~~\n\nA few things to note about the template definition.\n\nEach TOML ``tools.conhead.header`` section has a few options:\n\n-   **extensions:** A list of extensions that the header definition\n    applies to.\n-   **template:** The header template for this header definition.\n    This is the text that is applied to files that have the\n    indicated extensions.\n\nHeader Templates\n~~~~~~~~~~~~~~~~\n\nNotice a few things about the header template.\n\n-   The text of the template is indented for better readability\n    withing the ``pyproject.toml`` configuration file, however\n    ``conhead`` de-indents this text for you.\n-   The template contains a field that is kept up to date in\n    the target source file. In this case the ``{{YEAR}}`` field\n    writes the current year into every new template. If a file\n    already contains a header with the year in it, and the year\n    is different from the current year, it is updated to show\n    a range of years. For example, a new template would have\n    the ``{{YEAR}}`` field replaced with ``2020`` if it was\n    first written in ``2020``. When the header is then updated\n    in ``2022``, this field is rewritten as ``2020-2022``.\n-   If you need to write some text that contains certain\n    characters used to describe fields, you must escape them.\n    Examples are ``\\{``, ``\\}`` and `\\\\`. These characters will\n    appear in the rendered header without the preceding slash.\n\nUsage\n-----\n\nLet\'s say there is a python file without a header at ``hello.py``:\n\n.. code-block:: python\n\n\n    def hello():\n        print("Greetings!")\n\nYou can apply the ``hashhead`` header template defined in\n``pyproject.toml`` and view the results by:\n\n.. code-block:: shell\n\n    $ conhead hello.py\n    WARNING: missing header: hello.py\n\n    $ cat hello.py\n    # Copyright 2022 Organized Organization\n    # SPDX-License-Identifier: Apache-2.0\n\n\n    def hello():\n        print("Greetings!")\n\n``conhead`` will recognize the header if you apply it to ``hello.py``\nagain and will not write a second header.\n\n.. code-block:: shell\n\n    $ conhead hello.py\n\n    $ cat hello.py\n    # Copyright 2022 Organized Organization\n    # SPDX-License-Identifier: Apache-2.0\n\n\n    def hello():\n        print("Greetings!")\n\nLinks\n-----\n\n-   Changes: https://github.com/slobberchops/conhead/blob/main/CHANGES.rst\n-   PyPI Releases: https://pypi.org/project/conhead/\n-   Source Code: https://github.com/slobberchops/conhead\n-   Issue Tracker: https://github.com/slobberchops/conhead/issues\n',
    'author': 'Rafe Kaplan',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/slobberchops/conhead',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
