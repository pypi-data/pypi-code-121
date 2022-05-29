# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['resourceez']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'resourceez',
    'version': '0.1.0',
    'description': 'A slim package for declaratively expressing, serialising and deserialising REST resources.',
    'long_description': None,
    'author': 'tjweldon',
    'author_email': 'tomd90@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
