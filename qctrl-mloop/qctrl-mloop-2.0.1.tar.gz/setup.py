# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qctrlmloop']

package_data = \
{'': ['*']}

install_requires = \
['M-LOOP>=3.2.1,<3.3.0',
 'numpy>=1.21.5,<2.0.0',
 'qctrl>=18.0.0,<19.0.0',
 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'qctrl-mloop',
    'version': '2.0.1',
    'description': 'Q-CTRL Python M-LOOP',
    'long_description': '# Q-CTRL M-LOOP\n\nThe Q-CTRL M-LOOP Python package allows you to integrate Boulder Opal\nautomated closed-loop optimizers with automated closed-loop optimizations\nmanaged by the open-source package M-LOOP.\n',
    'author': 'Q-CTRL',
    'author_email': 'support@q-ctrl.com',
    'maintainer': 'Q-CTRL',
    'maintainer_email': 'support@q-ctrl.com',
    'url': '',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
