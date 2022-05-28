# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['push_plan']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['push-plan = push_plan.console:run']}

setup_kwargs = {
    'name': 'push-plan',
    'version': '0.1.1',
    'description': 'Archive and publish status to finger.farm',
    'long_description': "# push-plan: Finger.farm status updater\nProgram to archive `~/plan` & `~/project` files and push their latest content to finger.farm finger\nhosting service.\n\n## Usage\nCopy `doc/sample-config.toml` as `~/.config/push-plan/config.toml`. Modify values appropriately,\nespecially user name and API token command. Default config uses `gopass` to access the credential.\n\nCreate plan and project file as specified in the config file. Modify them as required. Use the \ncommand thereafter as follows:\n\n```\nusage: push-plan [-h] [--no-save] [--no-push] [--skip-check] [-d]\n\nRecord and update finger status\n\noptions:\n  -h, --help    show this help message and exit\n  --no-save     Don't save status. Push previously saved status.\n  --no-push     Don't push status.\n  --skip-check  Skip check for change in status.\n  -d, --debug   Print config info for debugging\n```\n\nThe files will be backed up in the specified archive directory prior to uploading online.\n\n## Development\nDevelopment happens over [sourcehut](https://sr.ht/~gokuldas/push-plan/). Discussion and\ncollaboration are over [~gokuldas/projects mailing list](mailto:~gokuldas/projects@lists.sr.ht).\nTask and bug tracking is done on [dedicated tracker](https://todo.sr.ht/~gokuldas/push-plan).\n\n## License\nCopyright (C) 2022 Gokul Das B\n\nThis program is distributed under GPLv3 license. Refer LICENSE file for details.\n",
    'author': 'Gokul Das B',
    'author_email': 'dev@gokuldas.space',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sr.ht/~gokuldas/push-plan/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
