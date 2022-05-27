# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['RPA', 'RPA.PDF', 'RPA.PDF.keywords']

package_data = \
{'': ['*'], 'RPA.PDF': ['assets/*']}

install_requires = \
['fpdf2>=2.5.2,<3.0.0',
 'pdfminer.six==20201018',
 'pypdf2>=1.27.4,<2.0.0,!=1.27.10,!=1.27.11',
 'robotframework-pythonlibcore>=3.0.0,<4.0.0',
 'robotframework>=4.0.0,!=4.0.1,<6.0.0',
 'rpaframework-core>=9.0.0,<10.0.0']

setup_kwargs = {
    'name': 'rpaframework-pdf',
    'version': '4.0.0',
    'description': 'PDF library of RPA Framework',
    'long_description': 'rpaframework-pdf\n================\n\nThis library enables various PDF features with `RPA Framework`_\nlibraries, such as locating text by label.\n\n.. _RPA Framework: https://rpaframework.org\n',
    'author': 'RPA Framework',
    'author_email': 'rpafw@robocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rpaframework.org/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
