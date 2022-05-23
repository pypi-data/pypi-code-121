# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['th2_box_descriptor_generator']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'th2-box-descriptor-generator',
    'version': '0.0.1.dev2370769627',
    'description': 'Python plugin to generate gRPC packages description',
    'long_description': '# th2-box-descriptor-generator-py',
    'author': 'TH2-devs',
    'author_email': 'th2-devs@exactprosystems.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/th2-net/th2-box-descriptor-generator-py',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
