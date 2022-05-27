# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['RPA', 'RPA.Windows', 'RPA.Windows.keywords', 'RPA.scripts']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.4.0,<0.5.0',
 'pynput-robocorp-fork>=4.0.0,<5.0.0',
 'robotframework-pythonlibcore>=3.0.0,<4.0.0',
 'robotframework>=4.0.0,!=4.0.1,<6.0.0',
 'rpaframework-core>=9.0.0,<10.0.0',
 'uiautomation>=2.0.15,<3.0.0']

extras_require = \
{':python_full_version < "3.7.6" and sys_platform == "win32" or python_full_version > "3.7.6" and python_full_version < "3.8.1" and sys_platform == "win32" or python_full_version > "3.8.1" and sys_platform == "win32"': ['pywin32>=300,<304'],
 ':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.7,<0.8'],
 ':sys_platform == "win32"': ['comtypes==1.1.11', 'psutil>=5.9.0,<6.0.0']}

entry_points = \
{'console_scripts': ['windows-record = RPA.scripts.record:main']}

setup_kwargs = {
    'name': 'rpaframework-windows',
    'version': '5.0.0',
    'description': 'Windows library for RPA Framework',
    'long_description': 'rpaframework-windows\n====================\n\nThis library enables Windows automation for the  `RPA Framework`_\nlibraries based on `uiautomation`_ dependency.\n\n.. _RPA Framework: https://rpaframework.org\n.. _uiautomation: https://github.com/yinkaisheng/Python-UIAutomation-for-Windows\n',
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
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
