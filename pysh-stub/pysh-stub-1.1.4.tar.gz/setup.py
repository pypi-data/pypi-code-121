# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysh']

package_data = \
{'': ['*']}

install_requires = \
['ideas>=0.0.37,<0.0.38',
 'tomlkit>=0.10.0,<0.11.0',
 'typer[all]>=0.4.0,<0.5.0',
 'typing-extensions>=4.2.0,<5.0.0']

entry_points = \
{'console_scripts': ['pysh = pysh.pysh:main']}

setup_kwargs = {
    'name': 'pysh-stub',
    'version': '1.1.4',
    'description': 'A bunch of shortcuts and import magic to simplify scripting in python',
    'long_description': '# Warning\n`pysh-stub` is deprecated and will be deleted. Please, use [pysh](https://pypi.org/projects/pysh) instead.\n\n# Pysh\nBash is said to be the opposite of riding the bike -- you have to re-learn it every time. So if we\'re doing anything more complex than running a few commands, chances are google will be needed. But if we switch to python, then the reverse is true -- python is a bit too cumbersome for simple scripts. I try to alleviate this problem by making it easier to use bash from python.\n\nIt was inspired by Jupyter\'s way of handling bash.\n\n## Installation\n```bash\npip install pysh-stub\n```\n## Quickstart\n* If you have a hello_world.pysh file with the contents below, you can run it using `pysh hello_world.pysh`:\n```bash\n!echo Hello World\nprint("Hello World")\n```\n* Most bash is going to be one-to-one translatable to pysh by putting exclamation marks at the beginning of each line:\n```bash\n!ls\n!cp some_file some/place\n```\n* It has most of the variables (\\$@, \\$#, $1, $2, etc) you would expect:\n```bash\n!echo $*\n```\n* You can also access python variables from bash using f-string notation\n```bash\nmy_file = "~/some/file" + ".txt"\n!cp {my_file} {my_file + ".bak"}\n```\n* If you wish to get the output of any command into a python variable, you can use double exclamation mark:\n```bash\n# Note that the default output of ls is silenced when !! are used\nlines = !!ls -lA\nfor line in lines.splitlines():\n    print(line)\n```\n## Builtins\nI consider the most comfortable way to write python scripts is to import os, pathlib, sys, and re first. Thus, all of these modules are pre-imported. However, instead of "pathlib.Path", we have "P". \n\nI also import typer as I consider it to be the most concise way to write any command line application.\n\nIf you wish to customize how you call bash subprocesses, you can use the builtin "sh" function. It supports all the same arguments as subprocess.run but has text=True and shell=True by default.\n\n## Magical Commands\nWe use subprocess.run to run bash commands but that has a few quirks. If you modify the process info in any way within the subprocess (cd, set, unset, etc), this information will not change for the currently running process. Hence we have a few magical commands that do not create a subprocess but instead use roughly equivalent python constructs.\n\nHere\'s a list of all the magical commands and the approximate conversions we apply to them:\n| Original        | Converted                                 |\n| -----------     | -----------                               |\n| !cd arg         | os.chdir(arg)                             |\n| !set -e         | \\_\\_pysh_check_returncodes\\_\\_.set(True)  |\n| !set +e         | \\_\\_pysh_check_returncodes\\_\\_.set(False) |\n| !exit arg       | sys.exit(int(arg))                        |\n## Notes on syntax\n* Each bash call is parsed until the end of the line so they are closer to statements than expressions. Hence the following is not possible:\n```bash\nprint(!!ls)\n```\n* Because we use f-strings to interface between python and bash, you will have to escape non-formatting "{" and "}" by typing them twice. You will also have to wrap these characters in quotes because prior to converting bash into executable format, we tokenize the entire file as if it was valid python. I.e. Unclosed braces, parenthesis, etc will cause a tokenize.TokenError.\n```bash\n# The invalid ways to do it\n!echo {\n!echo {{\n\n# The valid way to do it\n!echo "{{"\n```\n## FAQ\n* If you have any questions, encounter any bugs or want to suggest/contribute new features, please, use the issues in the github repository',
    'author': 'Stanislav Zmiev',
    'author_email': 'szmiev2000@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Ovsyanka83/pysh',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
