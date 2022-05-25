# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gobotz_rabbitmq']

package_data = \
{'': ['*']}

install_requires = \
['aioamqp>=0.15.0,<0.16.0', 'build>=0.8.0,<0.9.0', 'ujson>=5.3.0,<6.0.0']

setup_kwargs = {
    'name': 'gobotz-rabbitmq',
    'version': '0.0.10',
    'description': 'aioamqp wrapper for rabbitmq',
    'long_description': None,
    'author': 'GoBotz',
    'author_email': 'info@gobotz.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
