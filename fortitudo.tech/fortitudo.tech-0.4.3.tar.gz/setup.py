# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tech']

package_data = \
{'': ['*'], 'tech': ['data/*']}

install_requires = \
['cvxopt>=1.2,<2.0', 'pandas>=1.3.4,<2.0.0', 'scipy>=1.6,<2.0']

setup_kwargs = {
    'name': 'fortitudo.tech',
    'version': '0.4.3',
    'description': 'Investment and risk technologies maintained by Fortitudo Technologies.',
    'long_description': 'Fortitudo Technologies Open Source\n==================================\n\nThis package allows users to freely explore open-source implementations of some\nof our fundamental technologies under the `GNU General Public License, Version 3 \n<https://www.gnu.org/licenses/gpl-3.0.html>`_.\n\nFortitudo Technologies is a fintech company offering novel investment technologies\nas well as quantitative and digitalization consultancy to the investment\nmanagement industry. For more information, please visit our `website \n<https://fortitudo.tech>`_.\n\nThis package is intended for advanced users who are comfortable specifying\nportfolio constraints and Entropy Pooling views using matrices and vectors.\nThis gives full flexibility in relation to working with these technologies and\nallows users to build their own high-level interfaces if they wish to do so.\n\nInstallation Instructions\n-------------------------\n\nInstallation can be done via pip::\n\n   pip install fortitudo.tech\n\nFor best performance, we recommend that you install the package in a `conda environment\n<https://conda.io/projects/conda/en/latest/user-guide/concepts/environments.html>`_\nand let conda handle the installation of dependencies before installing the\npackage using pip. You can do this by following these steps::\n\n   conda create -n fortitudo.tech python scipy pandas -y\n   conda activate fortitudo.tech\n   conda install -c conda-forge cvxopt=1.3 -y\n   pip install fortitudo.tech\n\nContributing\n------------\n\nYou are welcome to contribute to this package by forking the `fortitudo.tech \nGitHub repository <https://github.com/fortitudo-tech/fortitudo.tech>`_ and\ncreating pull requests. Pull requests should always be sent to the dev branch.\nWe especially appreciate contributions in relation to packaging, e.g., making\nthe package available on conda-forge.\n\nUsing the conda environment specified in the requirements.yml file and located\nin the root directory of the repository is the easiest way to start contributing\nto the code::\n\n    conda env create --file requirements.yml\n\nThe style guide mostly follows `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_,\nbut it uses some important modifications that can be found in .vscode/settings.json.\nIf you use Visual Studio Code, you can use these settings to make sure that\nyour code follows the basic rules of the style guide. The most important\nmodifications/additions are:\n\n1) We allow line length to be 99 characters for both code and docstrings,\n2) We allow the use of capital I as a variable,\n3) We use type hints introduced in `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_,\n4) We do not group operators according to priority.\n\nWe generally follow naming conventions with descriptive variable and function\nnames, but we often use short variable names for the very mathematical parts of\nthe code to replicate the variables used in the references. We believe this makes\nit easier to link the code to the theory.\n\nWe encourage you to keep individual contributions small in addition to avoid\nimposing object-oriented design patterns. We are unlikely to accept contributions\nthat use inheritance without very good reasons and encourage you to use composition\ninstead.\n\nCode of Conduct\n---------------\n\nWe welcome feedback and bug reports, but we have very limited resources for\nsupport and feature requests. If you experience bugs with some of the upstream\npackages, please report them directly to the maintainers of the upstream packages.\n\nDisclaimer\n----------\n\nThis package is completely separate from our proprietary solution and therefore\nnot representative of the functionality offered in the Investment Analysis module.\nIf you are an institutional investor and want to experience how these technologies\ncan be used in very elegant ways, please `request a demo of the Investment Analysis\nmodule <https://fortitudo.tech/#contact>`_.\n',
    'author': 'Fortitudo Technologies',
    'author_email': 'software@fortitudo.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://fortitudo.tech',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
