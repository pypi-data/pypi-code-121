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
    'version': '0.1.0',
    'description': 'Archive and publish status to finger.farm',
    'long_description': None,
    'author': 'Gokul Das B',
    'author_email': 'dev@gokuldas.space',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
