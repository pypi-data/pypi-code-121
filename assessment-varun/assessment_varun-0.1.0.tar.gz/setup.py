# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['assessment_varun']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'assessment-varun',
    'version': '0.1.0',
    'description': 'oops and pandas',
    'long_description': None,
    'author': 'varun1423',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
