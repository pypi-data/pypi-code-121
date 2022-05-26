# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['smartinput',
 'smartinput.handlers',
 'smartinput.rgb',
 'smartinput.rgb.effects',
 'smartinput.server',
 'smartinput.settings',
 'smartinput.tests']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.1.2,<3.0.0',
 'Pillow>=9.1.1,<10.0.0',
 'PyAutoGUI>=0.9.53,<0.10.0',
 'PyYAML>=6.0,<7.0',
 'pyserial>=3.5,<4.0',
 'requests>=2.27.1,<3.0.0',
 'sacn>=1.8.1,<2.0.0']

entry_points = \
{'console_scripts': ['smartinput_ng_daemon = smartinput:run']}

setup_kwargs = {
    'name': 'smartinput-ng-daemon',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'niwla23',
    'author_email': 'alwin@cloudserver.click',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
