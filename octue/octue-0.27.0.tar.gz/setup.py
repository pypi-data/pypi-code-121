# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['octue',
 'octue.cloud',
 'octue.cloud.deployment',
 'octue.cloud.deployment.google',
 'octue.cloud.deployment.google.cloud_run',
 'octue.cloud.deployment.google.dataflow',
 'octue.cloud.pub_sub',
 'octue.cloud.storage',
 'octue.essentials',
 'octue.migrations',
 'octue.mixins',
 'octue.resources',
 'octue.templates',
 'octue.templates.template-child-services.elevation_service',
 'octue.templates.template-child-services.parent_service',
 'octue.templates.template-child-services.wind_speed_service',
 'octue.templates.template-python-fractal',
 'octue.templates.template-python-fractal.fractal',
 'octue.templates.template-using-manifests',
 'octue.templates.template-using-manifests.cleaner',
 'octue.utils']

package_data = \
{'': ['*'],
 'octue.templates.template-child-services.parent_service': ['data/input/*'],
 'octue.templates.template-python-fractal': ['data/configuration/*'],
 'octue.templates.template-using-manifests': ['data/configuration/*',
                                              'data/input/*',
                                              'data/input/raw_met_mast_data/*',
                                              'data/input/raw_met_mast_data/08DEC/*']}

install_requires = \
['Flask==2.0.3',
 'click>=7,<9',
 'coolname>=1.1,<2.0',
 'google-auth>=1.27.0,<3',
 'google-cloud-pubsub>=2.5,<3.0',
 'google-cloud-secret-manager>=2.3,<3.0',
 'google-cloud-storage>=1.35.1,<3',
 'google-crc32c>=1.1,<2.0',
 'gunicorn>=20.1,<21.0',
 'python-dateutil>=2.8,<3.0',
 'pyyaml>=6,<7',
 'twined>=0.5.0,<0.6.0']

extras_require = \
{'dataflow': ['apache-beam[gcp]>=2.37,<3.0'], 'hdf5': ['h5py>=3.6,<4.0']}

entry_points = \
{'console_scripts': ['octue = octue.cli:octue_cli']}

setup_kwargs = {
    'name': 'octue',
    'version': '0.27.0',
    'description': 'A package providing template applications for data services, and a python SDK to the Octue API.',
    'long_description': '[![PyPI version](https://badge.fury.io/py/octue.svg)](https://badge.fury.io/py/octue)\n[![Release](https://github.com/octue/octue-sdk-python/actions/workflows/release.yml/badge.svg)](https://github.com/octue/octue-sdk-python/actions/workflows/release.yml)\n[![codecov](https://codecov.io/gh/octue/octue-sdk-python/branch/main/graph/badge.svg?token=4KdR7fmwcT)](https://codecov.io/gh/octue/octue-sdk-python)\n[![Documentation Status](https://readthedocs.org/projects/octue-python-sdk/badge/?version=latest)](https://octue-python-sdk.readthedocs.io/en/latest/?badge=latest)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n# octue-sdk-python <span><img src="http://slurmed.com/fanart/javier/213_purple-fruit-snake.gif" alt="Purple Fruit Snake" width="100"/></span>\n\nUtilities for running python based data services, digital twins and applications. [Documentation is here!](https://octue-python-sdk.readthedocs.io/en/latest/)\n\nBased on the [twined](https://twined.readthedocs.io/en/latest/) library for data validation.\n\n## Installation and usage\nFor usage as a scientist or engineer, run the following command in your environment:\n```shell\npip install octue\n```\n\nThe command line interface (CLI) can then be accessed via:\n```shell\noctue-app --help\n```\n\n## Developer notes\n\n### Installation\nFor development, run the following from the repository root, which will editably install the package:\n```bash\npip install -r requirements-dev.txt\n```\n\n### Testing\nThese environment variables need to be set to run the tests:\n* `GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service/account/file.json`\n* `TEST_PROJECT_NAME=<name-of-google-cloud-project-to-run-pub-sub-tests-on>`\n\nThen, from the repository root, run\n```bash\npython3 -m unittest\n```\n\n**Documentation for use of the library is [here](https://octue-python-sdk.readthedocs.io). You don\'t need to pay attention to the following unless you plan to develop `octue-sdk-python` itself.**\n\n### Pre-Commit\n\nYou need to install pre-commit to get the hooks working. Do:\n```\npip install pre-commit\npre-commit install\n```\n\nOnce that\'s done, each time you make a commit, the following checks are made:\n\n- valid github repo and files\n- code style\n- import order\n- PEP8 compliance\n- documentation build\n- branch naming convention\n\nUpon failure, the commit will halt. **Re-running the commit will automatically fix most issues** except:\n\n- The flake8 checks... hopefully over time Black (which fixes most things automatically already) will negate need for it.\n- You\'ll have to fix documentation yourself prior to a successful commit (there\'s no auto fix for that!!).\n\nYou can run pre-commit hooks without making a commit, too, like:\n```\npre-commit run black --all-files\n```\nor\n```\n# -v gives verbose output, useful for figuring out why docs won\'t build\npre-commit run build-docs -v\n```\n\n\n### Contributing\n\n- Please raise an issue on the board (or add your $0.02 to an existing issue) so the maintainers know\nwhat\'s happening and can advise / steer you.\n\n- Create a fork of octue-sdk-python, undertake your changes on a new branch, (see `.pre-commit-config.yaml` for branch naming conventions). To run tests and make commits,\nyou\'ll need to do something like:\n```\ngit clone <your_forked_repo_address>    # Fetches the repo to your local machine\ncd octue-sdk-python                     # Move into the repo directory\npyenv virtualenv 3.8 myenv              # Makes a virtual environment for you to install the dev tools into. Use any python >= 3.8\npyend activate myenv                    # Activates the virtual environment so you don\'t screw up other installations\npip install -r requirements-dev.txt     # Installs the testing and code formatting utilities\npre-commit install                      # Installs the pre-commit code formatting hooks in the git repo\n```\n\n- Adopt a Test Driven Development approach to implementing new features or fixing bugs.\n\n- Ask the maintainers *where* to make your pull request. We\'ll create a version branch, according to the\nroadmap, into which you can make your PR. We\'ll help review the changes and improve the PR.\n\n- Once checks have passed, test coverage of the new code is 100%, documentation is updated and the Review is passed, we\'ll merge into the version branch.\n\n- Once all the roadmapped features for that version are done, we\'ll release.\n\n\n### Release process\n\nThe process for creating a new release is as follows:\n\n1. Check out a branch for the next version, called `vX.Y.Z`\n2. Create a Pull Request into the `main` branch.\n3. Undertake your changes, committing and pushing to branch `vX.Y.Z`\n4. Ensure that documentation is updated to match changes, and increment the changelog. **Pull requests which do not update documentation will be refused.**\n5. Ensure that test coverage is sufficient. **Pull requests that decrease test coverage will be refused.**\n6. Ensure code meets style guidelines (pre-commit scripts and flake8 tests will fail otherwise)\n7. Address Review Comments on the PR\n8. Ensure the version in `setup.py` is correct and matches the branch version.\n9. Merge to master. Successful test, doc build, flake8 and a new version number will automatically create the release on pypi.\n10. Go to code > releases and create a new release on GitHub at the same SHA.\n\n\n## Documents\n\n### Building documents automatically\n\nThe documentation will build automatically in a pre-configured environment when you make a commit.\n\nIn fact, the way pre-commit works, you won\'t be allowed to make the commit unless the documentation builds,\nthis way we avoid getting broken documentation pushed to the main repository on any commit sha, so we can rely on\nbuilds working.\n\n\n### Building documents manually\n\n**If you did need to build the documentation**\n\nInstall `doxgen`. On a mac, that\'s `brew install doxygen`; other systems may differ.\n\nInstall sphinx and other requirements for building the docs:\n```\npip install -r docs/requirements.txt\n```\n\nRun the build process:\n```\nsphinx-build -b html docs/source docs/build\n```\n\nTom Clark, founder of octue\nWe\'ve been developing open-source tools to make\nit easy for normal, mortal scientists and\nengineers to easily create, use and connect\n',
    'author': 'Thomas Clark',
    'author_email': 'support@octue.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.github.com/octue/octue-sdk-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
