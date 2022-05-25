# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['roxieapi',
 'roxieapi.cadata',
 'roxieapi.commons',
 'roxieapi.input_builder',
 'roxieapi.tool_adapter']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.1,<2.0.0',
 'plotly>=5.6.0,<6.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'roxie-api',
    'version': '0.0.4',
    'description': 'A Python API for ROXIE to build a model data input, modify cable database file, and control simulation with a tool adapter',
    'long_description': '# ROXIE API\n\nThis is a project for extraction of ROXIE API from MagNum API for code sharing with the ROXIE team.',
    'author': 'mmaciejewski',
    'author_email': 'michal.maciejewski@ief.ee.ethz.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.cern.ch/roxie/roxie-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
