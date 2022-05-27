# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['glassnodeapi']

package_data = \
{'': ['*']}

install_requires = \
['iso8601>=1.0.2,<2.0.0', 'pandas>=1.4.2,<2.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'glassnodeapi',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'なるみ',
    'author_email': 'narumi@maicoin.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
