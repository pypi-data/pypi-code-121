# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['commander']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'commander-py',
    'version': '0.1.7',
    'description': 'A very simple tool to create beautiful console application by using native argparse.',
    'long_description': '# Commander\n\n> A very simple tool to create beautiful console application by using native argparse.\n\n| Project       | Tabler                                       |\n|---------------|----------------------------------------------|\n| Author        | Özcan Yarımdünya                             |\n| Documentation | https://ozcanyarimdunya.github.io/commander/ |\n| Source code   | https://github.com/ozcanyarimdunya/commander |\n\n`commander` is a library that you can create beautiful class based cli application by using `argparse`.\n\n## Installation\n\nOnly `python3.7+` required, no extra dependencies.\n\n```shell\npip install commander-py\n```\n\n## Usage\n\nBasic usage, let\'s greet someone :)\n\nCreate a file named `myapp.py`.\n\nImport required classes from `commander` library\n\n```python\nfrom commander import Application\nfrom commander import Command\n```\n\nDefine your first command.\n\n1. `create` is the method where you define your cli arguments\n2. `handle` is the method where you use entered arguments.\n\n```python\nclass GreetCommand(Command):\n    name = "greet"\n    description = "Greet command"\n\n    def create(self):\n        """Create your cli arguments here"""\n\n        self.add_argument("-n", "--name", help="Name of sample")\n\n    def handle(self, **arguments):\n        """Do things with your arguments here"""\n\n        name = arguments["name"]\n        print(f"Greetings {name} :)")\n\n```\n\nCreate your commander application and register the command then run.\n\n```python\nif __name__ == \'__main__\':\n    app = Application(name="myapp", description="My first commander application")\n    app.register(GreetCommand)\n    app.run()\n```\n\n**Now test your first application**\n\nSimple usage.\n\n```text\n# Command\n$ python myapp.py greet -n "John Doe"\n\n# Output\nGreetings John Doe :)\n```\n\nSubcommand `greet` subcommand also have its own help function.\n\n```text\n# Command\n$ python myapp.py greet --help\n\n# Output\nUSAGE: myapp greet [-h] [-n NAME]\n\nGreeting command\n\nOPTIONAL ARGUMENTS:\n  -h, --help            show this help message and exit\n  -n NAME, --name NAME  Name of sample\n```\n\nThe main application `myapp` has its own help function, you can see `greet` command in the _AVAILABLE COMMANDS_ section\n\n```text\n# Command\n$ python myapp.py --help\n\n# Output\nUSAGE: myapp [-h] {greet}\n\nMy first commander application\n\nOPTIONAL ARGUMENTS:\n  -h, --help       show this help message and exit\n\nAVAILABLE COMMANDS:\n  greet   Greeting command\n```\n\n## Test\n\nThis project using `pytest` and `pytest-cov`.\n\n```shell\nmake test\n```\n\n## Documentation\n\n**Live preview**\n\n```shell\nmake serve-docs\n```\n\n**Building**\n\n```shell\nbuild-docs\n```\n\n## LICENSE\n\n```text\nMIT License\n\nCopyright (c) 2022 yarimdunya.com\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n\n```\n',
    'author': 'Özcan Yarımdünya',
    'author_email': 'ozcanyd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ozcanyarimdunya.github.io/commander/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
