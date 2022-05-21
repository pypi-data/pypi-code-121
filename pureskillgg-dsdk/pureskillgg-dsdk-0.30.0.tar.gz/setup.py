# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pureskillgg_dsdk',
 'pureskillgg_dsdk.adx',
 'pureskillgg_dsdk.ds_io',
 'pureskillgg_dsdk.ds_models',
 'pureskillgg_dsdk.tome']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.12.32,<2.0.0',
 'pandas>=1.2.1,<2.0.0',
 'pyarrow>=8.0.0,<9.0.0',
 'python-rapidjson>=1.6,<2.0',
 'structlog>=21.5.0,<22.0.0']

setup_kwargs = {
    'name': 'pureskillgg-dsdk',
    'version': '0.30.0',
    'description': 'Python Data Science Development Kit.',
    'long_description': 'PureSkill.gg Data Science Development Kit\n=========================================\n\n|PyPI| |GitHub Actions|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/pureskillgg-dsdk.svg\n   :target: https://pypi.python.org/pypi/pureskillgg-dsdk\n   :alt: PyPI\n.. |GitHub Actions| image:: https://github.com/pureskillgg/dsdk/workflows/main/badge.svg\n   :target: https://github.com/pureskillgg/dsdk/actions\n   :alt: GitHub Actions\n\nPython Data Science Development Kit.\n\nDescription\n-----------\n\nDo data science for games.\n\nInstallation\n------------\n\nThis package is registered on the `Python Package Index (PyPI)`_\nas pureskillgg_dsdk_.\n\nInstall it with\n\n::\n\n    $ poetry add pureskillgg_dsdk\n\n.. _pureskillgg_dsdk: https://pypi.python.org/pypi/pureskillgg-dsdk\n.. _Python Package Index (PyPI): https://pypi.python.org/\n\nDevelopment and Testing\n-----------------------\n\nQuickstart\n~~~~~~~~~~\n\n::\n\n    $ git clone https://github.com/pureskillgg/dsdk.git\n    $ git lfs install\n    $ git lfs pull\n    $ cd dsdk\n    $ poetry install\n\nRun each command below in a separate terminal window:\n\n::\n\n    $ make watch\n\nPrimary development tasks are defined in the `Makefile`.\n\nSource Code\n~~~~~~~~~~~\n\nThe `source code`_ is hosted on GitHub.\nClone the project with\n\n::\n\n    $ git clone https://github.com/pureskillgg/dsdk.git\n    $ git lfs install\n    $ git lfs pull\n\n.. _source code: https://github.com/pureskillgg/dsdk\n\nRequirements\n~~~~~~~~~~~~\n\nYou will need `Python 3`_ and Poetry_.\n\nInstall the development dependencies with\n\n::\n\n    $ poetry install\n\n.. _Poetry: https://poetry.eustace.io/\n.. _Python 3: https://www.python.org/\n\nTests\n~~~~~\n\nLint code with\n\n::\n\n    $ make lint\n\n\nRun tests with\n\n::\n\n    $ make test\n\nRun tests on changes with\n\n::\n\n    $ make watch\n\nPublishing\n~~~~~~~~~~\n\nUse the bump2version_ command to release a new version.\nPush the created git tag which will trigger a GitHub action.\n\n.. _bump2version: https://github.com/c4urself/bump2version\n\nPublishing may be triggered using on the web\nusing a `workflow_dispatch on GitHub Actions`_.\n\n.. _workflow_dispatch on GitHub Actions: https://github.com/pureskillgg/dsdk/actions?query=workflow%3Aversion\n\nGitHub Actions\n--------------\n\n*GitHub Actions should already be configured: this section is for reference only.*\n\nThe following repository secrets must be set on GitHub Actions.\n\n- ``PYPI_API_TOKEN``: API token for publishing on PyPI.\n\nThese must be set manually.\n\nSecrets for Optional GitHub Actions\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nThe version and format GitHub actions\nrequire a user with write access to the repository\nincluding access to read and write packages.\nSet these additional secrets to enable the action:\n\n- ``GH_USER``: The GitHub user\'s username.\n- ``GH_TOKEN``: A personal access token for the user.\n- ``GIT_USER_NAME``: The name to set for Git commits.\n- ``GIT_USER_EMAIL``: The email to set for Git commits.\n- ``GPG_PRIVATE_KEY``: The `GPG private key`_.\n- ``GPG_PASSPHRASE``: The GPG key passphrase.\n\n.. _GPG private key: https://github.com/marketplace/actions/import-gpg#prerequisites\n\nContributing\n------------\n\nPlease submit and comment on bug reports and feature requests.\n\nTo submit a patch:\n\n1. Fork it (https://github.com/pureskillgg/dsdk/fork).\n2. Create your feature branch (`git checkout -b my-new-feature`).\n3. Make changes.\n4. Commit your changes (`git commit -am \'Add some feature\'`).\n5. Push to the branch (`git push origin my-new-feature`).\n6. Create a new Pull Request.\n\nLicense\n-------\n\nThis Python package is licensed under the MIT license.\n\nWarranty\n--------\n\nThis software is provided by the copyright holders and contributors "as is" and\nany express or implied warranties, including, but not limited to, the implied\nwarranties of merchantability and fitness for a particular purpose are\ndisclaimed. In no event shall the copyright holder or contributors be liable for\nany direct, indirect, incidental, special, exemplary, or consequential damages\n(including, but not limited to, procurement of substitute goods or services;\nloss of use, data, or profits; or business interruption) however caused and on\nany theory of liability, whether in contract, strict liability, or tort\n(including negligence or otherwise) arising in any way out of the use of this\nsoftware, even if advised of the possibility of such damage.\n',
    'author': 'PureSkill.gg',
    'author_email': 'contact@pureskill.gg',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pureskillgg/dsdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
