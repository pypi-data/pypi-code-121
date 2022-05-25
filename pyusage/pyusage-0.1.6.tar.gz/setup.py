# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyusage', 'usage']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4.11.3,<5.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=12.3.0,<13.0.0',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['usage = usage.cli:usage']}

setup_kwargs = {
    'name': 'pyusage',
    'version': '0.1.6',
    'description': '',
    'long_description': '# PyUsage\n',
    'author': 'PyUsage Team',
    'author_email': 'packages@pyusage.org',
    'maintainer': 'Balaji Veeramani',
    'maintainer_email': 'bveeramani@berkeley.edu',
    'url': 'https://pyusage.org',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
