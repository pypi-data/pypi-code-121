# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['treat', 'treat.mock', 'treat.pytest', 'treat.ui', 'treat.utils']

package_data = \
{'': ['*']}

install_requires = \
['cleo>=1.0.0a3,<2.0.0',
 'coverage>=6.2,<7.0',
 'pprintpp>=0.4.0,<0.5.0',
 'pytest>=6.2.5,<7.0.0']

entry_points = \
{'pytest11': ['treat = treat.pytest.plugin']}

setup_kwargs = {
    'name': 'treat',
    'version': '0.1.0',
    'description': 'Delicious tests for Python',
    'long_description': 'None',
    'author': 'Sébastien Eustace',
    'author_email': 'sebastien@eustace.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
