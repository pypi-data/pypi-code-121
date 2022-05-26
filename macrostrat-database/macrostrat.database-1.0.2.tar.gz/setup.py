# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['macrostrat', 'macrostrat.database', 'macrostrat.database.mapper']

package_data = \
{'': ['*']}

install_requires = \
['GeoAlchemy2>=0.9.4,<0.10.0',
 'SQLAlchemy-Utils>=0.37.0,<0.38.0',
 'SQLAlchemy>=1.4.26,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'macrostrat.utils>=1.0.0,<2.0.0',
 'migra>=3.0.1621480950,<4.0.0',
 'psycopg2-binary>=2.9.1,<3.0.0',
 'schemainspect>=3.0.1616029793,<4.0.0',
 'sqlparse>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'macrostrat.database',
    'version': '1.0.2',
    'description': 'A small library based on SQLAlchemy to assist with common database tasks.',
    'long_description': None,
    'author': 'Daven Quinn',
    'author_email': 'dev@davenquinn.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
