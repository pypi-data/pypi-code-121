# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['clophfit', 'clophfit.old']

package_data = \
{'': ['*'], 'clophfit.old': ['bash/*']}

install_requires = \
['corner>=2.2.1,<3.0.0',
 'emcee>=3.1.1,<4.0.0',
 'lmfit>=1.0.3,<2.0.0',
 'numpy>=1.17,<2.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.3.3,<2.0.0',
 'rpy2>=3.4.5,<4.0.0',
 'scipy>=1.7.1,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'sympy>=1.9,<2.0',
 'tqdm>=4.62.3,<5.0.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['clop = clophfit.cli:run']}

setup_kwargs = {
    'name': 'clophfit',
    'version': '0.3.3',
    'description': 'Cli for fitting macromolecule pH titration or binding assays data e.g. fluorescence spectra.',
    'long_description': '|PyPI| |Tests| |RtD| |zenodo|\n\nClopHfit\n========\n\nCli for fitting macromolecule pH titration or binding assay data, e.g.\nfluorescence spectra.\n\n- Version: “0.3.3”\n\n\nFeatures\n--------\n\n- Plate Reader data Parser.\n- Perform non-linear least square fitting.\n- Extract and fit pH and chloride titrations of GFP libraries.\n\n  - For 2 labelblocks (e.g. 400, 485 nm) fit data separately and globally.\n  - Estimate uncertainty using  bootstrap.\n  - Subtract buffer for each titration point.\n  - Report controls e.g. S202N, E2 and V224Q.\n  - Correct for dilution of titration additions.\n  - Plot data when fitting fails and save txt file anyway.\n\n\nUsage\n-----\n\n- Extract and fit titrations from a list of tecan files collected at various\n  pH or chloride concentrations::\n\n   clop prtecan --help\n\n  For example::\n\n\tclop prtecan list.pH -k ph --scheme ../scheme.txt --dil additions.pH --norm \\\n\t  --out prova2 --Klim 6.8,8.4 --sel 7.6,20\n\n  To reproduce older pr.tecan add `--no-weight` option::\n\n\tclop prtecan list.pH -k ph --scheme ../scheme.txt --no-bg --no-weight \\\n\t  --out 4old --Klim 6.8,8.4 --sel 7.6,20\n\n- Predict chloride dissociation constant `K_d` at given pH::\n\n   clop eq1 --help\n\nTo use clophfit in a project::\n\n  from clophfit import prtecan, binding\n\n\nInstallation\n------------\n\nYou can get the library directly from |PyPI|::\n\n    pip install clophfit\n\n\nDevelopment\n-----------\n\nPrepare a virtual development environment and test first installation::\n\n   pyenv install 3.10.2\n   poetry env use 3.10\n   poetry install\n   poetry run pytest -v\n\nMake sure::\n\n   pre-commit install\n   pre-commit install --hook-type commit-msg\n\nFor Jupyter_::\n\n   poetry run python -m ipykernel install --user --name="cloph-310"\n\nTo generate docs::\n\n   poetry run nox -rs docs\n\nWhen needed (e.g. API updates)::\n\n   sphinx-apidoc -f -o docs/api/ src/clophfit/\n\nUse commitizen and github-cli to release::\n\n   poetry run cz bump --changelog-to-stdout --files-only (--prerelease alpha) --increment MINOR\n   gh release create (--target devel) v0.3.0a0\n\n\nDevelopment environment\n~~~~~~~~~~~~~~~~~~~~~~~\n\n* Test automation requires nox and nox-poetry.\n\n* Formatting with black[jupyter] configured in pyproject.\n\n* Linters are configured in .flake8 .darglint and .isort.cfg and include::\n\n  - flake8-isort\n  - flake8-bugbear\n  - flake8-docstrings\n  - darglint\n  - flake8-eradicate\n  - flake8-comprehensions\n  - flake8-pytest-style\n  - flake8-annotations (see mypy)\n  - flake8-rst-docstrings\n\n\t- rst-lint\n\n* pre-commit configured in .pre-commit-config.yaml activated with::\n\n  - pre-commit install\n  - commitizen install --hook-type commit-msg\n\n* Tests coverage (pytest-cov) configured in .coveragerc.\n\n* Type annotation configured in mypy.ini.\n\n* Commitizen_ also used to bump version::\n\n\tcz bump --changelog-to-stdout --files-only --prerelease alpha --increment MINOR\n\n  * need one-time initialization::\n\n\t  (cz init)\n\n* xdoctest\n\n* sphinx with pydata-sphinx-theme and sphinx-autodoc-typehints. (nbsphinx, sphinxcontrib-plantuml)::\n\n\tmkdir docs; cd docs\n\tsphinx-quickstart\n\n  Edit conf.py ["sphinx.ext.autodoc"] and index.rst [e.g. api/modules]::\n\n    sphinx-apidoc -f -o docs/api/ src/clophfit/\n\n* CI/CD configured in .github/workflows::\n\n\ttests.yml\n\trelease.yml\n\n  Remember to update tools version e.g. nox_poetry==0.9.\n\nWhat is missing to modernize_:\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n- coveralls/Codecov\n- release drafter; maybe useful when merging pr into main.\n- readthedocs or ghpages?\n  https://www.docslikecode.com/articles/github-pages-python-sphinx/\n\n\nCode of Conduct\n---------------\n\nEveryone interacting in the readme_renderer project\'s codebases, issue trackers,\nchat rooms, and mailing lists is expected to follow the `PSF Code of Conduct`_.\n\n   ..\n\t  .. image:: https://readthedocs.org/projects/prtecan/badge/?version=latest\n\t\t\t  :target: https://readthedocs.org/projects/prtecan/?badge=latest\n\t\t\t  :alt: Documentation Status\n\n\n\n.. |Tests| image:: https://github.com/darosio/ClopHfit/actions/workflows/tests.yml/badge.svg\n   :target: https://github.com/darosio/ClopHfit/actions/workflows/tests.yml\n.. |PyPI| image:: https://img.shields.io/pypi/v/ClopHfit.svg\n   :target: https://pypi.org/project/ClopHfit/\n.. |RtD| image:: https://readthedocs.org/projects/clophfit/badge/\n   :target: https://clophfit.readthedocs.io/\n.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.6354112.svg\n   :target: https://doi.org/10.5281/zenodo.6354112\n\n\n.. _Commitizen: https://commitizen-tools.github.io/commitizen/\n.. _Jupyter: https://jupyter.org/\n.. _modernize: https://cjolowicz.github.io/posts/hypermodern-python-06-ci-cd/\n.. _PSF Code of Conduct: https://github.com/pypa/.github/blob/main/CODE_OF_CONDUCT.md\n',
    'author': 'daniele arosio',
    'author_email': 'daniele.arosio@cnr.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/darosio/ClopHfit',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>3.8,<3.11',
}


setup(**setup_kwargs)
