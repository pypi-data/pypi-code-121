# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tardis',
 'tardis.clients',
 'tardis.database',
 'tardis.ingestors',
 'tardis.managers',
 'tardis.models',
 'tardis.models.exchange',
 'tardis.models.outputs',
 'tardis.syncs']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.36,<2.0.0',
 'dask[dataframe]==2020.12.0',
 'pandas==1.3.4',
 'pg8000>=1.26.1,<2.0.0',
 'py_vollib>=1.0.1,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.27.1,<3.0.0',
 'tardis-dev>=2.0.0-alpha.10,<3.0.0',
 'typedframe>=0.6.2,<0.7.0']

setup_kwargs = {
    'name': 'tardis-ingestors',
    'version': '0.3.0',
    'description': 'Tardis.dev ingestors for processed data',
    'long_description': None,
    'author': 'miguel-bm',
    'author_email': 'miguel.blanco.marcos@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
