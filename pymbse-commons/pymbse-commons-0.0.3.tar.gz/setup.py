# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymbse', 'pymbse.commons']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pymbse-commons',
    'version': '0.0.3',
    'description': '',
    'long_description': '# PyMBSE Commons\n\nProject with common functions used across all projects in the CHART-MagNum group.\n\n',
    'author': 'mmaciejewski',
    'author_email': 'michal.maciejewski@ief.ee.ethz.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.cern.ch/chart-magnum/pymbse-commons',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
