# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hamstercage', 'hamstercage.tests']

package_data = \
{'': ['*'], 'hamstercage.tests': ['repo/tags/all/*', 'repo/tags/foo/*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'importlib-resources>=5.7.1,<6.0.0']

entry_points = \
{'console_scripts': ['hamstercage = hamstercage:__main__.main']}

setup_kwargs = {
    'name': 'hamstercage',
    'version': '0.0.9',
    'description': 'Pets not cattle. A straightforward way to manage configuration files.',
    'long_description': None,
    'author': 'Stefan Bethke',
    'author_email': 'stb@lassitu.de',
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
