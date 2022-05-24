# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['eomap_models', 'eomap_models.altimetry']

package_data = \
{'': ['*']}

install_requires = \
['geojson-pydantic==0.3.1', 'pydantic==1.7.3']

setup_kwargs = {
    'name': 'eomap-models',
    'version': '0.1.14',
    'description': '',
    'long_description': None,
    'author': 'Luis Coelho',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
