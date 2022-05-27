# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['slap',
 'slap.ext',
 'slap.ext.application',
 'slap.ext.changelog_update_automation',
 'slap.ext.checks',
 'slap.ext.project_handlers',
 'slap.ext.release',
 'slap.ext.repository_handlers',
 'slap.ext.repository_hosts',
 'slap.install',
 'slap.python',
 'slap.util',
 'slap.util.external']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=4.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'cleo>=1.0.0a4',
 'databind>=2.0.0,<3.0.0',
 'flit>=3.6.0,<4.0.0',
 'nr.util>=0.8.4,<1.0.0',
 'poetry-core>=1.1.0a6,<2.0.0',
 'ptyprocess>=0.7.0,<0.8.0',
 'pygments>=2.11.2,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'setuptools>=39.1.0',
 'tomli>=2.0.0,<3.0.0',
 'tomlkit>=0.10.1,<0.11.0',
 'tqdm>=4.64.0,<5.0.0',
 'twine>=3.7.0,<4.0.0']

entry_points = \
{'console_scripts': ['slap = slap.__main__:main'],
 'slap.plugins.application': ['add = slap.ext.application.add:AddCommandPlugin',
                              'changelog = '
                              'slap.ext.application.changelog:ChangelogCommandPlugin',
                              'check = '
                              'slap.ext.application.check:CheckCommandPlugin',
                              'info = '
                              'slap.ext.application.info:InfoCommandPlugin',
                              'init = '
                              'slap.ext.application.init:InitCommandPlugin',
                              'install = '
                              'slap.ext.application.install:InstallCommandPlugin',
                              'link = '
                              'slap.ext.application.link:LinkCommandPlugin',
                              'publish = '
                              'slap.ext.application.publish:PublishCommandPlugin',
                              'release = '
                              'slap.ext.application.release:ReleaseCommandPlugin',
                              'report = '
                              'slap.ext.application.report:ReportPlugin',
                              'run = slap.ext.application.run:RunCommandPlugin',
                              'test = '
                              'slap.ext.application.test:TestCommandPlugin',
                              'venv = slap.ext.application.venv:VenvPlugin'],
 'slap.plugins.changelog_update_automation': ['github-actions = '
                                              'slap.ext.changelog_update_automation.github_actions:GithubActionsChangelogUpdateAutomationPlugin'],
 'slap.plugins.check': ['changelog = '
                        'slap.ext.checks.changelog:ChangelogValidationCheckPlugin',
                        'general = slap.ext.checks.general:GeneralChecksPlugin',
                        'poetry = slap.ext.checks.poetry:PoetryChecksPlugin',
                        'release = '
                        'slap.ext.checks.release:ReleaseChecksPlugin'],
 'slap.plugins.project': ['flit = '
                          'slap.ext.project_handlers.flit:FlitProjectHandler',
                          'poetry = '
                          'slap.ext.project_handlers.poetry:PoetryProjectHandler',
                          'setuptools = '
                          'slap.ext.project_handlers.setuptools:SetuptoolsProjectHandler'],
 'slap.plugins.release': ['changelog_release = '
                          'slap.ext.release.changelog:ChangelogReleasePlugin',
                          'source_code_version = '
                          'slap.ext.release.source_code_version:SourceCodeVersionReferencesPlugin'],
 'slap.plugins.repository': ['default = '
                             'slap.ext.repository_handlers.default:DefaultRepositoryHandler'],
 'slap.plugins.repository_host': ['github = '
                                  'slap.ext.repository_hosts.github:GithubRepositoryHost'],
 'slap.plugins.version_incrementing_rule': ['major = '
                                            'slap.ext.version_incrementing_rule:major',
                                            'minor = '
                                            'slap.ext.version_incrementing_rule:minor',
                                            'patch = '
                                            'slap.ext.version_incrementing_rule:patch',
                                            'premajor = '
                                            'slap.ext.version_incrementing_rule:premajor',
                                            'preminor = '
                                            'slap.ext.version_incrementing_rule:preminor',
                                            'prepatch = '
                                            'slap.ext.version_incrementing_rule:prepatch',
                                            'prerelease = '
                                            'slap.ext.version_incrementing_rule:prerelease']}

setup_kwargs = {
    'name': 'slap-cli',
    'version': '1.6.15',
    'description': 'Slap is a command-line utility for developing Python applications.',
    'long_description': '# Slap\n\n<img src="docs/content/img/logo.svg" style="height: 200px !important">\n\n  [PEP 517]: https://peps.python.org/pep-0517/\n\nSlap is a command-line tool to simplify command workflows in the development of Python projects\nindependent of the [PEP 517][] build backend being used, capable of managing single- and multi-project\nrepositories.\n\n## Installation\n\nI recommend installing Slap using Pipx. (Requires Python 3.10 or higher)\n\n    $ pipx install slap-cli\n\n> __Note__: Currently Slap relies on an alpha version of `poetry-core` (`^1.1.0a6`). If you install it into\n> the same environment as Poetry itself, you may also need to use an alpha version of Poetry (e.g. `1.2.0a2`).\n>\n> If you use Slap in GitHub Actions, try one of the actions provided by Slap directly:\n>\n> * [`NiklasRosenstein/slap@gha/install/v1`](https://niklasrosenstein.github.io/slap/guides/github/#install-slap)\n> * [`NiklasRosenstein/slap@gha/changelog/update/v1`](https://niklasrosenstein.github.io/slap/guides/github/#update-changelogs)\n\n## Documentation\n\nYou can find the documentation for Slap here: <https://niklasrosenstein.github.io/slap/>\n\nCheck out the [Getting started](https://niklasrosenstein.github.io/slap/getting-started/) guide.\n\n## Feature Matrix\n\n| Feature | Poetry | Documentation |\n| ------- | ------ | ------------- |\n| Manage structured changelog entries | ❌ | [slap changelog](https://niklasrosenstein.github.io/slap/commands/changelog/) |\n| Show project details | ❌ | [slap info](https://niklasrosenstein.github.io/slap/commands/info/) |\n| Build and publish to PyPI using Twine | ✅ (single project only) | [slap publish](https://niklasrosenstein.github.io/slap/commands/publish/) |\n| Create a new release (bump version numbersr)| ❌ (sub-par support) | [slap release](https://niklasrosenstein.github.io/slap/commands/release/) |\n| Run a command configured in `pyproject.toml` | ❌ | [slap run](https://niklasrosenstein.github.io/slap/commands/run/) |\n| Run tests configured in `pyproject.toml` | ❌ | [slap test](https://niklasrosenstein.github.io/slap/commands/test/) |\n| Manage Python virtualenv\'s | ✅ (but out-of-worktree) | [slap venv](https://niklasrosenstein.github.io/slap/commands/venv/) |\n| Generate a dependencies report | ❌ | [slap report dependencies](https://niklasrosenstein.github.io/slap/commands/report/) |\n\n| Feature / Build backend | Flit  | Poetry  | Setuptools  | Documentation |\n| ----------------------- | ----- | ------- | ----------- | --------- |\n| Add dependency | ✅ | ✅ | ❌ | [slap add](https://niklasrosenstein.github.io/slap/commands/add/) |\n| Sanity check project configuration | | ✅ | | [slap check](https://niklasrosenstein.github.io/slap/commands/check/) |\n| Bootstrap project files | | ✅ | | [slap init](https://niklasrosenstein.github.io/slap/commands/init/) |\n| Install projects using Pip | ✅ | ✅ | ✅ | [slap install](https://niklasrosenstein.github.io/slap/commands/install/) |\n| Symlink projects (editable installs) | ✅ | ✅ | ✅ | [slap link](https://niklasrosenstein.github.io/slap/commands/link/) |\n| Bump interdependencies in mono-repository | ✅ (not tested regularly) | ✅ | ✅ (partial) | [slap release](https://niklasrosenstein.github.io/slap/commands/release/) |\n\n> __Legend__: ✅ explicitly supported, ❌ explicitly not supported, (blank) not relevant or currently not supported\n\n## Issues / Suggestions / Contributions\n\n  [GitHub Issues]: https://github.com/NiklasRosenstein/slap/issues\n  [GitHub Discussions]: https://github.com/NiklasRosenstein/slap/discussions\n  [GitHub Repository]: https://github.com/NiklasRosenstein/slap\n\nSlap is currently very opinionated by the fact that I built it as my personal workflow tool, but I welcome\nsuggestions and contributions, and I am hopeful it will be useful to a wider audience than myself.\n\nPlease report any issues you encounter via [GitHub Issues][]. Feel free to use the [GitHub Discussions][] forum\nto ask questions or make suggestions on new features (e.g. if you would like a new build backend to be supported?).\nLastly, feel free to submit pull requests to the [GitHub Repository][].\n\n## FAQ\n\n### Why "Slap"?\n\nFinding a good, catchy name that also types easily in the terminal and is not already widely used isn\'t easy, ok?\n\n### What makes this different to the Poetry CLI?\n\nSome people might find this similar to tools like Poetry, and while there is some overlap in functionality, Slap is\n**not a build backend** and is more targeted towards library development. In fact, most of my projects use Poetry as\nthe build backend but I never even once interact with the Poetry CLI throughout the lifetime of the project.\n\nThe most notable differences to Poetry are\n\n* Supports mono-repositories (i.e. multiple related Python projects in the same repository), to the extent that it\n  bumps version numbers of project inter-dependencies and installs your projects in topological order\n* Supports development installs independent of the build backend (yes; this means you can install Poetry packages\n  in editable mode even though the Poetry backend right now does not support editable installs)\n* Slap\'s version bump command (`slap release`) updates the version not just in your `pyproject.toml` but also the\n  `__version__` in your source code as well as in related projects (see mono-repositories above) and any additional\n  references you can configure via Regex patterns\n* Does not automagically create a virtual environment for you when instal your project(s); instead, it errors when\n  you try to install into a non-virtual Python environment and gives you an easy-to-use tool to create and activate\n  virtual environments (and allowing multiple environments per project as well as global environments)\n* Uses Pip to install your project(s), unlike Poetry which comes with its own dependency resolver and package\n  installer (which I personally have been having a lot of issues with in the past).\n* Does not have a concept of lock files\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
