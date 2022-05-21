# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['letsdebughelper', 'letsdebughelper.tests']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0', 'requests>=2.27.1,<3.0.0', 'six>=1.16.0,<2.0.0']

entry_points = \
{'console_scripts': ['lets-debug = letsdebughelper.letsdebug:main']}

setup_kwargs = {
    'name': 'lets-debug-helper',
    'version': '1.0.7',
    'description': "This is a cli tool that interacts with the Let's Debug API",
    'long_description': None,
    'author': 'Jeffrey Crane',
    'author_email': 'jediknight11206@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
