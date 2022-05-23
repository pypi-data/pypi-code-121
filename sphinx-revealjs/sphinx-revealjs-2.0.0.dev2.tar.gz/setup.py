# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinx_revealjs', 'sphinx_revealjs._ext', 'sphinx_revealjs.themes']

package_data = \
{'': ['*'],
 'sphinx_revealjs.themes': ['sphinx_revealjs/*', 'sphinx_revealjs/static/*']}

install_requires = \
['docutils', 'sphinx']

setup_kwargs = {
    'name': 'sphinx-revealjs',
    'version': '2.0.0.dev2',
    'description': 'Sphinx extension with theme to generate Reveal.js presentation',
    'long_description': "sphinx-revealjs\n===============\n\n.. image:: https://img.shields.io/pypi/v/sphinx-revealjs.svg\n    :target: https://pypi.org/project/sphinx-revealjs/\n\n.. image:: https://github.com/attakei/sphinx-revealjs/workflows/Testings/badge.svg\n    :target: https://github.com/attakei/sphinx-revealjs/actions\n\n.. image:: https://travis-ci.org/attakei/sphinx-revealjs.svg?branch=master\n    :target: https://travis-ci.org/attakei/sphinx-revealjs\n\n.. image:: https://readthedocs.org/projects/sphinx-revealjs/badge/?version=latest\n    :target: https://sphinx-revealjs.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n\nSphinx extension with theme to generate Reveal.js presentation\n\nOverview\n--------\n\nThis extension generate Reveal.js presentation\nfrom **standard** reStructuredText.\n\nIt include theses features.\n\n* Custom builder to translate from reST to reveal.js style HTML\n* Template to be enable to render presentation local independent\n\nFor more information, refer to `the documentation <https://sphinx-revealjs.readthedocs.io/>`_.\n\nInstallation\n------------\n\n.. code-block:: bash\n\n    $ pip install sphinx-revealjs\n\n\nUsage\n-----\n\n1. Create your sphinx documentation\n2. Edit `conf.py` to use this extension\n\n    .. code-block:: python\n\n        extensions = [\n            'sphinx_revealjs',\n        ]\n\n3. Write source for standard document style\n\n4. Build sources as Reveal.js presentation\n\n    .. code-block:: bash\n\n        $ make revealjs\n\nChange logs\n-----------\n\nSee `it <./CHANGES.rst>`_\n\nPolicy for following to Reveal.js version\n-----------------------------------------\n\nThis is implemented based Reveal.js.\nI plan to update it at patch-version for catch up when new Reveal.js version released.\n\n* If Reveal.js updated minor or patch version, sphinx-revealjs update patch version.\n* If Reveal.js updated major version, sphinx-revealjs update minor version with compatible for two versions.\n\nContributings\n-------------\n\nGitHub repository does not have reveal.js library.\n\nIf you use from GitHub and editable mode, Run ``tools/fetch_revealjs.py`` after install.\n\n.. code-block:: bash\n\n    $ git clone https://github.com/attakei/sphinx-revealjs\n    $ cd sphinx-revealjs\n    $ poetry install\n    $ poetry run python tools/fetch_revealjs.py\n\nCopyright\n---------\n\nApache-2.0 license. Please see `LICENSE <./LICENSE>`_.\n",
    'author': 'Kazuya Takei',
    'author_email': 'myself@attakei.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/attakei/sphinx-revealjs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
