# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hamstercage', 'hamstercage.tests']

package_data = \
{'': ['*'], 'hamstercage.tests': ['repo/tags/all/*', 'repo/tags/foo/*']}

install_requires = \
['PyYAML>=6.0,<7.0']

setup_kwargs = {
    'name': 'hamstercage',
    'version': '0.0.4',
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
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
