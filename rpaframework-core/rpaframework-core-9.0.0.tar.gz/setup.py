# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['RPA', 'RPA.core', 'RPA.core.locators', 'RPA.core.vendor', 'RPA.core.windows']

package_data = \
{'': ['*']}

install_requires = \
['pillow>=9.1.1,<10.0.0',
 'selenium>=3.141.0,<4.0.0',
 'webdrivermanager>=0.10.0,<0.11.0']

extras_require = \
{':python_full_version < "3.7.6" and sys_platform == "win32" or python_full_version > "3.7.6" and python_full_version < "3.8.1" and sys_platform == "win32" or python_full_version > "3.8.1" and sys_platform == "win32"': ['pywin32>=300,<304'],
 ':sys_platform == "win32"': ['psutil>=5.9.0,<6.0.0',
                              'uiautomation>=2.0.15,<3.0.0']}

setup_kwargs = {
    'name': 'rpaframework-core',
    'version': '9.0.0',
    'description': 'Core utilities used by RPA Framework',
    'long_description': 'rpaframework-core\n=================\n\nThis package is a set of core functionality and utilities used\nby `RPA Framework`_. It is not intended to be installed directly, but\nas a dependency to other projects.\n\n.. _RPA Framework: https://rpaframework.org\n',
    'author': 'RPA Framework',
    'author_email': 'rpafw@robocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rpaframework.org/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
