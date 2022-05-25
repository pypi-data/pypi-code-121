# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cycparser', 'cycparser.parsing', 'cycparser.repairing']

package_data = \
{'': ['*']}

install_requires = \
['gitchangelog>=3.0.4,<4.0.0']

setup_kwargs = {
    'name': 'cycparser',
    'version': '1.2.0',
    'description': '',
    'long_description': 'None',
    'author': 'Marvin van Aalst',
    'author_email': 'marvin.vanaalst@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
