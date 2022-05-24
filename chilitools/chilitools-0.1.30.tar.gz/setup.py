# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chilitools', 'chilitools.api', 'chilitools.settings', 'chilitools.utilities']

package_data = \
{'': ['*']}

install_requires = \
['coloredlogs>=15.0.1,<16.0.0',
 'pyperclip>=1.8.2,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'xmltodict>=0.12.0,<0.13.0']

extras_require = \
{'images': ['img2pdf>=0.4.4,<0.5.0', 'Pillow>=9.1.0,<10.0.0']}

setup_kwargs = {
    'name': 'chilitools',
    'version': '0.1.30',
    'description': 'A collection of tools for working with the CHILI publish REST API',
    'long_description': None,
    'author': 'Austin',
    'author_email': 'austin.meier@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
