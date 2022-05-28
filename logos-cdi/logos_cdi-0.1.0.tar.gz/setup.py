# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['logos_cdi']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['logos = logos_cdi.__main__:main']}

setup_kwargs = {
    'name': 'logos-cdi',
    'version': '0.1.0',
    'description': '',
    'long_description': "# logos_cdi\n\n\nSimple and powerful python container dependency injection module\n\n\n## installation\n\n```bash\n> poetry add logos_cdi\n```\n\n## usage\n\ncreate `main.py` file and create `logos_cdi.application:Application` instance with a modules for usage.\n\n```py\n\nfrom logos_cdi.application import Application\n\n\napp = Application([\n    'logos_cdi',\n    'logos_cdi.command'\n])\n\n```\n\nin your terminal with venv actived type `logos -h` command and press enter.\n\n```\n\n> logos -h\nusage: logos [-h] {} ...\n\noptions:\n  -h, --help  show this help message and exit\n\ncommand:\n  {}          command to execute\n\n```\n\nthis is your app's command manager all your commands you can see here\n\nPS. your commands are loaded from the modules used in the application, you can implement them, see `./logos_cdi/command.py` file to understand how to create a module.\n",
    'author': 'Elielton Kremer',
    'author_email': 'elielton@integra.do',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
