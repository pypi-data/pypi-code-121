# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cookiecutter_python',
 'cookiecutter_python.backend',
 'cookiecutter_python.hooks',
 'cookiecutter_python.{{ cookiecutter.project_slug }}.docs',
 'cookiecutter_python.{{ cookiecutter.project_slug }}.scripts',
 'cookiecutter_python.{{ cookiecutter.project_slug }}.src.{{ '
 'cookiecutter.pkg_name }}',
 'cookiecutter_python.{{ cookiecutter.project_slug }}.tests']

package_data = \
{'': ['*'],
 'cookiecutter_python': ['{{ cookiecutter.project_slug }}/*',
                         '{{ cookiecutter.project_slug }}/.github/workflows/*'],
 'cookiecutter_python.{{ cookiecutter.project_slug }}.docs': ['contents/*']}

install_requires = \
['click>=8,<9',
 'cookiecutter>=1.7.3,<2.0.0',
 'requests-futures>=1.0.0,<2.0.0',
 'software-patterns>=1.2.1,<2.0.0']

extras_require = \
{'docs': ['sphinx>=4.0,<5.0',
          'sphinx-autodoc-typehints>=1.10',
          'sphinx-rtd-theme==0.5.0',
          'sphinxcontrib-spelling>=7.3.3,<7.4.0'],
 'test': ['pytest>=6.2.4',
          'pytest-click>=1.1.0,<1.2.0',
          'pytest-cov>=2.12',
          'pytest-explicit>=1.0.1,<1.1.0',
          'pytest-xdist>=1.34'],
 'typing': ['pytest>=6.2.4',
            'pytest-click>=1.1.0,<1.2.0',
            'mypy>=0.950,<1.0',
            'types-requests>=2.27.26,<2.28.0']}

entry_points = \
{'console_scripts': ['generate-python = cookiecutter_python.__main__:main']}

setup_kwargs = {
    'name': 'cookiecutter-python',
    'version': '1.2.0',
    'description': 'Yet another modern Python Package (pypi) with emphasis in CI/CD and automation.',
    'long_description': 'Cookiecutter Python Package\n===========================\n\nPython Package (pypi) Cookiecutter, with emphasis on CI/CD and automation.\n\n.. start-badges\n\n| |build| |docs| |coverage| |ossf| |maintainability| |better_code_hub| |codacy| |tech-debt| |black|\n| |release_version| |wheel| |supported_versions| |gh-lic| |commits_since_specific_tag_on_master| |commits_since_latest_github_release|\n\n|\n| **Source:** https://github.com/boromir674/cookiecutter-python-package\n| **Docs:** https://python-package-generator.readthedocs.io/en/master/\n| **PyPI:** https://pypi.org/project/cookiecutter-python/\n| **CI:** https://github.com/boromir674/cookiecutter-python-package/actions/\n\n\nFeatures\n========\n\n1. Fresh **Python Package Project Generation**, "packaged" with a **Test Suite** and a **CI** Pipeline (see `Quickstart`_)\n2. **Python Package Template** (source code at `src/cookiecutter_python/`_) implemented as a `Cookiecutter`\n3. **Tested** on python versions **3.6, 2.7, 3.8, 3.9 and 3.10**, for both **"Linux"** and **"MacOS"** platforms (see `Test Workflow` on `CI`_)\n\n\nAuto Generated Sample Package **Biskotaki**\n-------------------------------------------\n\nCheck the **Biskotaki** *Python Package Project*, for a taste of the project structure and capabilities this Template can generate!\n\nIt it entirely generated using this **Python Package Template:**\n\n\n| **Source Code** hosted on *Github* at https://github.com/boromir674/biskotaki\n| **Python Package** hosted on *pypi.org* at https://pypi.org/project/biskotaki/\n| **CI Pipeline** hosted on *Github Actions* at https://github.com/boromir674/biskotaki/actions\n\n\nGenerated Python Package Features\n---------------------------------\n\n1. **Test Suite**, using `pytest`_, located in `tests` dir\n2. **Parallel Execution** of Unit Tests, on multiple cpu\'s\n3. **Documentation Pages**, hosted on `readthedocs` server, located in `docs` dir\n4. **Automation**, using `tox`_, driven by single `tox.ini` file\n\n   a. **Code Coverage** measuring\n   b. **Build Command**, using the `build`_ python package\n   c. **Pypi Deploy Command**, supporting upload to both `pypi.org`_ and `test.pypi.org`_ servers\n   d. **Type Check Command**, using `mypy`_\n   e. **Lint** *Check* and `Apply` commands, using `isort`_ and `black`_\n5. **CI Pipeline**, running on `Github Actions`_, defined in `.github/`\n\n   a. **Job Matrix**, spanning different `platform`\'s and `python version`\'s\n\n      1. Platforms: `ubuntu-latest`, `macos-latest`\n      2. Python Interpreters: `3.6`, `3.7`, `3.8`, `3.9`, `3.10`\n   b. **Parallel Job** execution, generated from the `matrix`, that runs the `Test Suite`\n\n\nQuickstart\n==========\n\nInstallation\n------------\n\n    .. code-block: shell\n\n        pip install --user cookiecutter-python\n\n\nUsage\n-----\n\nOpen a console/terminal and run:\n\n  .. code-block:: sh\n\n      generate-python\n\nNow, you should have generated a new Project for a Python Package, based on the `Template`_!\n\n    Just \'enter\' (`cd` into) the newly created directory, ie `cd <my-great-python-package>`.\n\n| Develop your package\'s **Source Code** (`business logic`) inside `src/my_great_python_package` dir :)\n| Develop your package\'s **Test Suite** (ie `unit-tests`, `integration tests`) inside `tests` dir :-)\n\n\nTry Running the Test Suite!\n\n    .. code-block:: shell\n\n        tox\n\n\nRead the Documentation\'s `Use Cases`_ section for more on how to leverage your generated Python Package features.\n\n\nLicense\n=======\n\n|gh-lic|\n\n* `GNU Affero General Public License v3.0`_\n\n\nFree/Libre and Open Source Software (FLOSS)\n-------------------------------------------\n\n|ossf|\n\n\nNotes\n=====\n\nCurrently, since the actual `cookiecutter` template does not reside on the `root` directory\nof the repository (but rather in `src/cookiecutter_python`), \'cloning\' the repository\nlocally is required at first.\n\nThis was demonstrated in the `Quickstart` section, as well.\n\nFor more complex use cases, you can modify the Template and also leverage all of\n`cookiecutter`\'s features, according to your needs.\n\n\n.. URL LINKS\n\n.. _Cookiecutter documentation: https://cookiecutter.readthedocs.io/en/stable/\n\n.. _CI: https://github.com/boromir674/cookiecutter-python-package/actions\n\n.. _tox: https://tox.wiki/en/latest/\n\n.. _pytest: https://docs.pytest.org/en/7.1.x/\n\n.. _build: https://github.com/pypa/build\n\n.. _pypi.org: https://pypi.org/\n\n.. _test.pypi.org: https://test.pypi.org/\n\n.. _mypy: https://mypy.readthedocs.io/en/stable/\n\n.. _Github Actions: https://github.com/boromir674/cookiecutter-python-package/actions\n\n.. _src/cookiecutter_python/: https://github.com/boromir674/cookiecutter-python-package/tree/master/src/cookiecutter_python\n\n.. _Template: https://github.com/boromir674/cookiecutter-python-package/tree/master/src/cookiecutter_python\n\n.. _Use Cases: https://python-package-generator.readthedocs.io/en/master/contents/30_usage/index.html#new-python-package-use-cases\n\n.. _GNU Affero General Public License v3.0: https://github.com/boromir674/cookiecutter-python-package/blob/master/LICENSE\n\n.. _isort: https://pycqa.github.io/isort/\n\n.. _black: https://black.readthedocs.io/en/stable/\n\n\n\n.. BADGE ALIASES\n\n.. Build Status\n.. Github Actions: Test Workflow Status for specific branch <branch>\n\n.. |build| image:: https://img.shields.io/github/workflow/status/boromir674/cookiecutter-python-package/Test%20Python%20Package/master?label=build&logo=github-actions&logoColor=%233392FF\n    :alt: GitHub Workflow Status (branch)\n    :target: https://github.com/boromir674/cookiecutter-python-package/actions/workflows/test.yaml?query=branch%3Amaster\n\n\n.. Documentation\n\n.. |docs| image:: https://img.shields.io/readthedocs/python-package-generator/master?logo=readthedocs&logoColor=lightblue\n    :alt: Read the Docs (version)\n    :target: https://python-package-generator.readthedocs.io/en/master/\n\n.. Code Coverage\n\n.. |coverage| image:: https://img.shields.io/codecov/c/github/boromir674/cookiecutter-python-package/master?logo=codecov\n    :alt: Codecov\n    :target: https://app.codecov.io/gh/boromir674/cookiecutter-python-package\n\n.. PyPI\n\n.. |release_version| image:: https://img.shields.io/pypi/v/cookiecutter_python\n    :alt: Production Version\n    :target: https://pypi.org/project/cookiecutter-python/\n\n.. |wheel| image:: https://img.shields.io/pypi/wheel/cookiecutter-python?color=green&label=wheel\n    :alt: PyPI - Wheel\n    :target: https://pypi.org/project/cookiecutter-python\n\n.. |supported_versions| image:: https://img.shields.io/pypi/pyversions/cookiecutter-python?color=blue&label=python&logo=python&logoColor=%23ccccff\n    :alt: Supported Python versions\n    :target: https://pypi.org/project/cookiecutter-python\n\n\n.. Github Releases & Tags\n\n.. |commits_since_specific_tag_on_master| image:: https://img.shields.io/github/commits-since/boromir674/cookiecutter-python-package/v1.2.0/master?color=blue&logo=github\n    :alt: GitHub commits since tagged version (branch)\n    :target: https://github.com/boromir674/cookiecutter-python-package/compare/v1.2.0..master\n\n.. |commits_since_latest_github_release| image:: https://img.shields.io/github/commits-since/boromir674/cookiecutter-python-package/latest?color=blue&logo=semver&sort=semver\n    :alt: GitHub commits since latest release (by SemVer)\n\n\n.. LICENSE (eg AGPL, MIT)\n.. Github License\n\n.. |gh-lic| image:: https://img.shields.io/github/license/boromir674/cookiecutter-python-package\n    :alt: GitHub\n    :target: https://github.com/boromir674/cookiecutter-python-package/blob/master/LICENSE\n\n\n.. Free/Libre Open Source Software\n.. Open Source Software Best Practices\n\n.. |ossf| image:: https://bestpractices.coreinfrastructure.org/projects/5988/badge\n    :alt: OpenSSF\n    :target: https://bestpractices.coreinfrastructure.org/en/projects/5988\n\n\n.. CODE QUALITY\n\n.. Better Code Hub\n.. Software Design Patterns\n\n.. |better_code_hub| image:: https://bettercodehub.com/edge/badge/boromir674/cookiecutter-python-package?branch=master\n    :alt: Better Code Hub\n    :target: https://bettercodehub.com/\n\n\n.. Codacy\n.. Code Quality, Style, Security\n\n.. |codacy| image:: https://app.codacy.com/project/badge/Grade/5be4a55ff1d34b98b491dc05e030f2d7\n    :alt: Codacy\n    :target: https://app.codacy.com/gh/boromir674/cookiecutter-python-package/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=boromir674/cookiecutter-python-package&amp;utm_campaign=Badge_Grade\n\n\n.. Code Climate CI\n.. Code maintainability & Technical Debt\n\n.. |maintainability| image:: https://api.codeclimate.com/v1/badges/1d347d7dfaa134fd944e/maintainability\n   :alt: Maintainability\n   :target: https://codeclimate.com/github/boromir674/cookiecutter-python-package/\n\n.. |tech-debt| image:: https://img.shields.io/codeclimate/tech-debt/boromir674/cookiecutter-python-package\n    :alt: Code Climate technical debt\n    :target: https://codeclimate.com/github/boromir674/cookiecutter-python-package/\n\n\n.. Code Style with Black\n\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :alt: Black\n    :target: https://github.com/psf/black\n',
    'author': 'Konstantinos Lampridis',
    'author_email': 'k.lampridis@hotmail.com',
    'maintainer': 'Konstantinos Lampridis',
    'maintainer_email': 'k.lampridis@hotmail.com',
    'url': 'https://github.com/boromir674/cookiecutter-python-package',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
