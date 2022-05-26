# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['runcommands',
 'runcommands.commands',
 'runcommands.completion',
 'runcommands.util']

package_data = \
{'': ['*'], 'runcommands.completion': ['bash/*', 'fish/*']}

install_requires = \
['com.wyattbaldwin.cached_property>=1.0,<2.0',
 'rich>=10.3.0,<11.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['run = runcommands.__main__:main',
                     'runcommand = runcommands.__main__:main',
                     'runcommands = runcommands.__main__:main',
                     'runcommands-complete = '
                     'runcommands.completion:complete.console_script',
                     'runcommands-complete-base-command = '
                     'runcommands.completion:complete_base_command.console_script']}

setup_kwargs = {
    'name': 'runcommands',
    'version': '1.0a69',
    'description': 'A framework for writing console scripts and running commands',
    'long_description': 'RunCommands\n+++++++++++\n\nA simple command runner that uses ``argparse`` from the Python standard\nlibrary under the hood. Runs on Python 3 only (3.6 and up). Uses annotations to\nconfigure options.\n\nThere are two basic use cases:\n\n1. Standalone console scripts (including scripts with subcommands).\n2. Collections of commands (similar to make, Fabric, etc).\n\nBuilding on these, especially #2, there are a couple of more advanced\nuse cases:\n\n1. A simple orchestration/deployment tool. If you have a simple build\n   process and just need to ``rsync`` some files to a server, a few\n   simple commands might be all you need.\n2. A wrapper for more sophisticated orchestration/deployment tools--an\n   alternative to the Bash scripts you might use to drive Ansible\n   playbooks and the like.\n\nBasic Usage\n===========\n\nDefine a command:\n\n.. code-block:: python\n\n    from runcommands import arg, command\n    from runcommands.commands import local\n\n    @command\n    def test(*tests: arg(help=\'Specific tests to run (instead of using discovery)\')):\n        if tests:\n            local((\'python\', \'-m\', \'unittest\', tests))\n        else:\n            local(\'python -m unittest discover .\')\n\nShow its help::\n\n    > run test -h\n    test [-h] [TESTS [TESTS ...]]\n\n    positional arguments:\n      TESTS       Specific tests to run (instead of using discovery)\n\n    optional arguments:\n      -h, --help  show this help message and exit\n\nRun it::\n\n    > run test\n    ..........\n    ----------------------------------------------------------------------\n    Ran 0 tests in 0.000s\n\n    OK\n\nCreate a standalone console script using a standard setuptools entry\npoint:\n\n.. code-block:: python\n\n    # setup.py\n    setup(\n        ...\n        entry_points="""\n        [console_scripts]\n        my-test-script = package.module:test.console_script\n\n        """\n    )\n\nRun it (after reinstalling the package)::\n\n    > my-test-script\n    ..........\n    ----------------------------------------------------------------------\n    Ran 0 tests in 0.000s\n\n    OK\n\nSee the `main documentation`_ for more information on installation,\ndefining & running commands, configuration, etc.\n\nFeatures\n========\n\n* Easily create standalone console scripts: simply define a function and\n  wrap it with the ``@command`` decorator.\n* Easily create standalone console scripts that have subcommands (a la\n  ``git``).\n* Create collections of commands (similar to make, Fabric, etc).\n* Run multiple commands in sequence: ``run build deploy``.\n* Uses ``argparse`` under the hood so command line usage is familiar.\n* Provides built-in help/usage for all commands via ``argparse``.\n* Provides command line completion (including example scripts for bash\n  and fish).\n\nDocumentation\n=============\n\nDetailed documentation is on `Read the Docs`_.\n\nLicense\n=======\n\nMIT. See the LICENSE file in the source distribution.\n\nTODO\n====\n\n* Improve command line completion\n* Add more documentation and examples\n* Write tests\n\n.. _main documentation: http://runcommands.readthedocs.io/\n.. _Read the Docs: `main documentation`_\n',
    'author': 'Wyatt Baldwin',
    'author_email': 'self@wyattbaldwin.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://runcommands.readthedocs.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
