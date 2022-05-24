# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sssom_schema', 'sssom_schema.src.sssom_schema.datamodel']

package_data = \
{'': ['*'],
 'sssom_schema': ['project/docs/*',
                  'project/docs/types/*',
                  'project/excel/*',
                  'project/graphql/*',
                  'project/jsonld/*',
                  'project/jsonschema/*',
                  'project/owl/*',
                  'project/prefixmap/*',
                  'project/protobuf/*',
                  'project/shacl/*',
                  'project/shex/*',
                  'project/sqlschema/*',
                  'src/CONFIG.yaml',
                  'src/docs/*',
                  'src/docs/explanation/*',
                  'src/linkml/*']}

install_requires = \
['linkml-runtime>=1.1.24,<2.0.0']

setup_kwargs = {
    'name': 'sssom-schema',
    'version': '0.1.1',
    'description': 'SSSOM is a Simple Standard for Sharing Ontology Mappings.',
    'long_description': None,
    'author': 'Nicolas Matentzoglu',
    'author_email': 'nicolas.matentzoglu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
