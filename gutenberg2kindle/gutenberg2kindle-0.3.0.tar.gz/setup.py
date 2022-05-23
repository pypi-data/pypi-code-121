# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gutenberg2kindle']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'usersettings>=1.1.5,<2.0.0']

entry_points = \
{'console_scripts': ['gutenberg2kindle = gutenberg2kindle.cli:main']}

setup_kwargs = {
    'name': 'gutenberg2kindle',
    'version': '0.3.0',
    'description': 'A small Python tool to download and send ebooks from Project Gutenberg to a Kindle email address via SMTP',
    'long_description': "# Gutenberg2Kindle\n\nA small Python tool to download and send ebooks from Project Gutenberg to a Kindle email address via SMTP\n\n## What's this?\n\n`gutenberg2kindle` is a small command-line interface tool that aims to automatically download an `.epub` book from [Project Gutenberg](https://www.gutenberg.org/)'s library of free books in the public domain, and then send the ebook's file to a Kindle email address (although, generally, it can be sent to any email address), with just one command.\n\nThe book is sent through a SMTP server with TLS, requiring the user to configure the server settings beforehand via tool commands.\n\n## Installation\n\nYou can use your Python package manager (e.g. [pip](https://pip.pypa.io/en/stable/)) to install `gutenberg2kindle`.\n\n```bash\npip install gutenberg2kindle\n```\n\n## Usage\n\n`gutenberg2kindle` comes with a command-line interface; its help text can be accessed via:\n\n```bash\ngutenberg2kindle --help\n```\n\nYou can check the tool's current configuration via:\n\n```bash\n# will print all config variables with their current values\ngutenberg2kindle get-config\n\n# will print only the value for the key you're specifying\ngutenberg2kindle get-config --name <key name>\n```\n\nYou can set a value for any of the settings via:\n\n```bash\ngutenberg2kindle set-config --name <key name> --value <key value>\n```\n\nOr you can do it all at once interactively, being able to check (and modify, if needed) the current config, just by running:\n\n```bash\ngutenberg2kindle interactive-config\n```\n\nFinally, once you're done configuring your project, you can send any ebook via its Project Gutenberg book ID (with flags `-b` or `--book-id`):\n\n```bash\ngutenberg2kindle send -b <book id as an integer, e.g. 1>\n```\n\nYou can send multiple books at the same time in the same run, the `-b` / `--book-id` flag accepts multiple arguments.\n\n```bash\ngutenberg2kindle send -b <first book id> [<second book id> <third book id>...]\n```\n\nNote that, if using Gmail as your SMTP server, you might need to set up an [App Password](https://support.google.com/accounts/answer/185833) to use instead of your regular password.\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Contributions for issues that are already open by maintainers are welcome and encouraged.\n\nPlease make sure to update tests as appropriate; a minimum coverage of 75% is expected (and enforced by Github Actions!).\n\n## License\n\nThis project is licensed under the [GNU Affero General Public License v3.0](https://github.com/aitorres/gutenberg2kindle/blob/main/LICENSE).\n",
    'author': 'Andrés Ignacio Torres',
    'author_email': 'dev@aitorres.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aitorres/gutenberg2kindle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
