# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fdk_rdf_parser',
 'fdk_rdf_parser.classes',
 'fdk_rdf_parser.parse_functions',
 'fdk_rdf_parser.rdf_utils',
 'fdk_rdf_parser.reference_data']

package_data = \
{'': ['*']}

install_requires = \
['isodate>=0.6.0,<0.7.0', 'rdflib>=6.0.2,<7.0.0', 'requests>=2.23.0,<3.0.0']

setup_kwargs = {
    'name': 'fdk-rdf-parser',
    'version': '2.1.6',
    'description': '',
    'long_description': None,
    'author': 'NilsOveTen',
    'author_email': 'nils.ove.tendenes@digdir.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
