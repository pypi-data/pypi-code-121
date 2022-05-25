# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modelon',
 'modelon.impact',
 'modelon.impact.client',
 'modelon.impact.client.jupyterhub',
 'modelon.impact.client.sal']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.23,<3.0', 'semantic_version>=2.8.5,<3.0.0']

setup_kwargs = {
    'name': 'modelon-impact-client',
    'version': '2.1.0b2',
    'description': 'Client library for easy scripting against Modelon Impact',
    'long_description': '# Modelon-impact-client\nClient library for easy scripting against Modelon Impact\n\n## Installation\n\nFor installation instructions and requirements, please refer to the [documentation](https://modelon-impact-client.readthedocs.io).\n\n## Develop\n\n### Devcontainer\nIf you are developing with VS Code you can use the devcontainer which gives gives you a ready to use environment for development. Just click the "Reopen in Container" button after opening the project in VS Code.\n\n#### Tips and tricks\nIt is possible to run the \'make\' commands listed bellow using the devcontainer. It will detect being in a container and bypass Docker parts of the commands.\n\nYou can open a project with the dev-container directly without having to open and then re-load. Standing in the project directory you can run:\n```\ndevcontainer open .\n```\nNote that this requires the [devcontainer-cli](https://code.visualstudio.com/docs/remote/devcontainer-cli).\n\nYou can add your own extensions to devcontainers. These extensions will be added for all devcontainers. First open your \'settings\' as JSON. Then, to add for example the "GitLens" extension, put the following at the bottom of the settings:\n```\n    ...\n    "remote.containers.defaultExtensions": ["eamodio.gitlens"]\n}\n```\nVS Code also have a `\'Install Local Extensions in \'Remote\'` command, but it must be repeated for each devcontainer and everytime a devcontainer is re-built.\n\n### Creating a shell\nModelon-impact-client is developed using a Docker container for all build tools.\nYou can get a shell into said container by running:\n\n```\nmake shell\n```\n\n### Manage dependencies\nDependencies are managed by poetry. Add dependencies by running \n`poetry add <package>`  or `poetry add <package> --dev` inside the shell\n\n### Running tests\n\nTests are executed by running `make test`. You can also run `make test-watch` to get a watcher\nthat continuously re-runs the tests.\n\n### Running lint\n```\nmake lint\n```\n\n## Build\n\nBuilding modelon-impact-client is done by running\n\n```\nmake wheel\n```\n\n## Release\n\nThe modelon-impact-client build process is a fully automated using `Semantic-release`.\n\nAutomation is enabled for:\n- Bumping version\n- Generate changelog\n\nThis is done based on git commit semantics as described here: https://semantic-release.gitbook.io/semantic-release/\n\nTo make a new release simply run:\n```\nmake publish\n```\n\nThis command will detect what branch you are on and your git history and make a appropriate release.\n\nCurrent configuration can be found in `.releaserc` and specifies that commits to branch `master` should be released and\ncommits to branch `beta` should be released as a `pre-release`.\n\nThis workflow make sure that no administrative time needs to be put into managing the release workflow.\n',
    'author': 'WEP',
    'author_email': 'impact@modelon.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.modelon.com/modelon-impact',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
