# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ipumspy', 'ipumspy.api']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'click>=7.0.0,<8.0.0',
 'pandas>=1.3.5,<2.0.0',
 'pyarrow>=3.0.0,<4.0.0',
 'requests>=2.25.1,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.0.1,<5.0.0'],
 'docs': ['Sphinx>=4.1.2,<5.0.0',
          'sphinx-autodoc-typehints>=1.12.0,<2.0.0',
          'sphinx-copybutton>=0.4.0,<0.5.0',
          'myst-parser>=0.15.2,<0.16.0',
          'furo>=2021.8.31,<2022.0.0']}

entry_points = \
{'console_scripts': ['ipums = ipumspy.cli:cli']}

setup_kwargs = {
    'name': 'ipumspy',
    'version': '0.2.1',
    'description': 'A collection of tools for working with IPUMS data',
    'long_description': None,
    'author': 'Kevin H. Wilson',
    'author_email': 'kevin_wilson@brown.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
