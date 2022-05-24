# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['prefect_extensions']

package_data = \
{'': ['*']}

install_requires = \
['prefect>=2.0b,<3.0', 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'prefect-extensions',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Daniel Neururer',
    'author_email': 'neud@zhaw.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
