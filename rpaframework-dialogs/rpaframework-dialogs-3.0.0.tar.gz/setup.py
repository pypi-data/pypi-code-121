# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['RPA', 'RPA.Dialogs']

package_data = \
{'': ['*']}

install_requires = \
['robocorp-dialog>=0.5.3,<0.6.0',
 'robotframework>=4.0.0,!=4.0.1,<6.0.0',
 'rpaframework-core>=9.0.0,<10.0.0']

setup_kwargs = {
    'name': 'rpaframework-dialogs',
    'version': '3.0.0',
    'description': 'Dialogs library of RPA Framework',
    'long_description': "rpaframework-dialogs\n====================\n\nThis library allows creating dynamic dialogs during Robot Framework\nexecutions, which can be used for showing information to users and\nrequesting input from them. It's a part of `RPA Framework`_.\n\n.. _RPA Framework: https://rpaframework.org\n",
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
