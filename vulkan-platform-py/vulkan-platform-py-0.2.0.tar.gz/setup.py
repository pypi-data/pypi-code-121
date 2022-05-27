# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vulkan_platform_py']

package_data = \
{'': ['*']}

install_requires = \
['GPUtil>=1.4.0,<2.0.0',
 'mypy>=0.960,<0.961',
 'py-cpuinfo>=8.0.0,<9.0.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'vulkan-platform-py',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Rayan Hatout',
    'author_email': 'rayan.hatout@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10',
}


setup(**setup_kwargs)
