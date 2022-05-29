# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libvcs', 'libvcs._internal', 'libvcs.cmd', 'libvcs.projects']

package_data = \
{'': ['*']}

extras_require = \
{':python_version == "3.10"': ['typing-extensions>=4.1.1,<5.0.0']}

setup_kwargs = {
    'name': 'libvcs',
    'version': '0.13.0a12',
    'description': 'Lite, typed, python library wrapper for git, svn, mercurial, etc.',
    'long_description': '# `libvcs` &middot; [![Python Package](https://img.shields.io/pypi/v/libvcs.svg)](https://pypi.org/project/libvcs/) [![License](https://img.shields.io/github/license/vcs-python/libvcs.svg)](https://github.com/vcs-python/libvcs/blob/master/LICENSE) [![Code Coverage](https://codecov.io/gh/vcs-python/libvcs/branch/master/graph/badge.svg)](https://codecov.io/gh/vcs-python/libvcs)\n\nlibvcs is a lite, [typed](https://docs.python.org/3/library/typing.html), pythonic wrapper for\n`git`, `hg`, and `svn`. Powers [vcspull](https://www.github.com/vcs-python/vcspull/).\n\n## Setup\n\n```console\n$ pip install --user libvcs\n```\n\nOpen up python:\n\n```console\n$ python\n```\n\nOr for nice autocompletion and highlighting:\n\n```console\n$ pip install --user ptpython\n```\n\n```console\n$ ptpython\n```\n\n## Commands (experimental)\n\nSimple [`subprocess`](https://docs.python.org/3/library/subprocess.html) wrappers around `git(1)`,\n`hg(1)`, `svn(1)`. Here is [`Git`](https://libvcs.git-pull.com/cmd/git.html#libvcs.cmd.git.Git) w/\n[`Git.clone`](http://libvcs.git-pull.com/cmd/git.html#libvcs.cmd.git.Git.clone):\n\n```python\nimport pathlib\nfrom libvcs.cmd.git import Git\n\ngit = Git(dir=pathlib.Path.cwd() / \'my_git_repo\')\ngit.clone(url=\'https://github.com/vcs-python/libvcs.git\')\n```\n\n## Projects\n\nCreate a\n[`GitProject`](https://libvcs.git-pull.com/projects/git.html#libvcs.projects.git.GitProject) object\nof the project to inspect / checkout / update:\n\n```python\nimport pathlib\nfrom libvcs.projects.git import GitProject\n\nrepo = GitProject(\n   url="https://github.com/vcs-python/libvcs",\n   dir=pathlib.Path().cwd() / "my_repo",\n   remotes={\n       \'gitlab\': \'https://gitlab.com/vcs-python/libvcs\'\n   }\n)\n```\n\nUpdate / clone repo:\n\n```python\n>>> r.update_repo()\n```\n\nGet revision:\n\n```python\n>>> r.get_revision()\nu\'5c227e6ab4aab44bf097da2e088b0ff947370ab8\'\n```\n\n## Donations\n\nYour donations fund development of new features, testing and support. Your money will go directly to\nmaintenance and development of the project. If you are an individual, feel free to give whatever\nfeels right for the value you get out of the project.\n\nSee donation options at <https://www.git-pull.com/support.html>.\n\n## More information\n\n- Python support: 3.9+, pypy\n- VCS supported: git(1), svn(1), hg(1)\n- Source: <https://github.com/vcs-python/libvcs>\n- Docs: <https://libvcs.git-pull.com>\n- Changelog: <https://libvcs.git-pull.com/history.html>\n- API:\n  - [`libvcs.cmd`](https://libvcs.git-pull.com/cmd/): Commands\n  - [`libvcs.projects`](https://libvcs.git-pull.com/projects/): High-level synchronization commands\n- Issues: <https://github.com/vcs-python/libvcs/issues>\n- Test Coverage: <https://codecov.io/gh/vcs-python/libvcs>\n- pypi: <https://pypi.python.org/pypi/libvcs>\n- Open Hub: <https://www.openhub.net/p/libvcs>\n- License: [MIT](https://opensource.org/licenses/MIT).\n\n[![Docs](https://github.com/vcs-python/libvcs/workflows/docs/badge.svg)](https://libvcs.git-pull.com/)\n[![Build Status](https://github.com/vcs-python/libvcs/workflows/tests/badge.svg)](https://github.com/vcs-python/libvcs/actions?query=workflow%3A%22tests%22)\n',
    'author': 'Tony Narlock',
    'author_email': 'tony@git-pull.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/vcs-python/libvcs/',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
