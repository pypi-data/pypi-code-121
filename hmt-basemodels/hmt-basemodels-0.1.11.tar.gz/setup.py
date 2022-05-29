# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['basemodels',
 'basemodels.manifest',
 'basemodels.manifest.data',
 'basemodels.pydantic',
 'basemodels.pydantic.manifest',
 'basemodels.pydantic.manifest.data']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=3.10.0,<4.0.0',
 'pydantic>=1.8.1,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'schematics>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'hmt-basemodels',
    'version': '0.1.11',
    'description': '',
    'long_description': None,
    'author': 'Intuition Machines, Inc',
    'author_email': 'support@hcaptcha.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
