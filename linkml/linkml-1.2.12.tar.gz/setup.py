# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['linkml',
 'linkml.generators',
 'linkml.generators.sqlalchemy',
 'linkml.reporting',
 'linkml.transformers',
 'linkml.utils',
 'linkml.validators',
 'linkml.workspaces',
 'linkml.workspaces.datamodel']

package_data = \
{'': ['*'], 'linkml.generators': ['docgen/*', 'javagen/*']}

install_requires = \
['antlr4-python3-runtime>=4.9.0,<4.10',
 'argparse>=1.4.0',
 'click>=7.0',
 'graphviz>=0.10.1',
 'hbreader',
 'isodate>=0.6.0',
 'jinja2',
 'jsonasobj2>=1.0.3,<2.0.0',
 'jsonschema>=3.0.1',
 'linkml-dataops',
 'linkml-runtime>=1.2.14,<2.0.0',
 'myst-parser',
 'openpyxl',
 'parse',
 'prefixcommons>=0.1.7',
 'pydantic',
 'pyjsg>=0.11.6',
 'pyshex>=0.7.20',
 'pyshexc>=0.8.3',
 'python-dateutil',
 'pyyaml',
 'rdflib>=6.0.0',
 'requests>=2.22',
 'sphinx-click',
 'sqlalchemy>=1.4.31',
 'watchdog>=0.9.0']

extras_require = \
{':extra == "docs"': ['sphinx', 'sphinx-rtd-theme']}

entry_points = \
{'console_scripts': ['gen-csv = linkml.generators.csvgen:cli',
                     'gen-doc = linkml.generators.docgen:cli',
                     'gen-excel = linkml.generators.excelgen:cli',
                     'gen-golr-views = linkml.generators.golrgen:cli',
                     'gen-graphql = linkml.generators.graphqlgen:cli',
                     'gen-graphviz = linkml.generators.dotgen:cli',
                     'gen-java = linkml.generators.javagen:cli',
                     'gen-json-schema = linkml.generators.jsonschemagen:cli',
                     'gen-jsonld = linkml.generators.jsonldgen:cli',
                     'gen-jsonld-context = '
                     'linkml.generators.jsonldcontextgen:cli',
                     'gen-linkml = linkml.generators.linkmlgen:cli',
                     'gen-markdown = linkml.generators.markdowngen:cli',
                     'gen-namespaces = linkml.generators.namespacegen:cli',
                     'gen-owl = linkml.generators.owlgen:cli',
                     'gen-prefix-map = linkml.generators.prefixmapgen:cli',
                     'gen-project = linkml.generators.projectgen:cli',
                     'gen-prolog = linkml.generators.lpgen:cli',
                     'gen-proto = linkml.generators.protogen:cli',
                     'gen-py-classes = linkml.generators.pythongen:cli',
                     'gen-pydantic = linkml.generators.pydanticgen:cli',
                     'gen-python = linkml.generators.pythongen:cli',
                     'gen-rdf = linkml.generators.rdfgen:cli',
                     'gen-shacl = linkml.generators.shaclgen:cli',
                     'gen-shex = linkml.generators.shexgen:cli',
                     'gen-sparql = linkml.generators.sparqlgen:cli',
                     'gen-sqla = linkml.generators.sqlalchemygen:cli',
                     'gen-sqlddl = linkml.generators.sqltablegen:cli',
                     'gen-sqlddl-legacy = linkml.generators.sqlddlgen:cli',
                     'gen-sqltables = linkml.generators.sqltablegen:cli',
                     'gen-sssom = linkml.generators.sssomgen:cli',
                     'gen-terminusdb = linkml.generators.terminusdbgen:cli',
                     'gen-typescript = linkml.generators.typescriptgen:cli',
                     'gen-yaml = linkml.generators.yamlgen:cli',
                     'gen-yuml = linkml.generators.yumlgen:cli',
                     'linkml-convert = linkml.utils.converter:cli',
                     'linkml-jsonschema-validate = '
                     'linkml.validators.jsonschemavalidator:cli',
                     'linkml-sparql-validate = '
                     'linkml.validators.sparqlvalidator:cli',
                     'linkml-sqldb = linkml.utils.sqlutils:main',
                     'linkml-validate = '
                     'linkml.validators.jsonschemavalidator:cli',
                     'linkml-ws = linkml.workspaces.cli:main',
                     'run-tutorial = linkml.utils.execute_tutorial:cli']}

setup_kwargs = {
    'name': 'linkml',
    'version': '1.2.12',
    'description': 'Linked Open Data Modeling Language',
    'long_description': '[![Pyversions](https://img.shields.io/pypi/pyversions/linkml.svg)](https://pypi.python.org/pypi/linkml)\n![](https://github.com/linkml/linkml/workflows/Build/badge.svg)\n[![PyPi](https://img.shields.io/pypi/v/linkml.svg)](https://pypi.python.org/pypi/linkml)\n[![badge](https://img.shields.io/badge/launch-binder-579ACA.svg)](https://mybinder.org/v2/gh/linkml/linkml/main?filepath=notebooks)\n[![DOI](https://zenodo.org/badge/13996/linkml/linkml.svg)](https://zenodo.org/badge/latestdoi/13996/linkml/linkml)\n[![PyPIDownloadsTotal](https://pepy.tech/badge/linkml)](https://pepy.tech/project/linkml)\n[![PyPIDownloadsMonth](https://img.shields.io/pypi/dm/linkml?logo=PyPI&color=blue)](https://pypi.org/project/linkml)\n\n\n# LinkML - Linked Data Modeling Language\n\nLinkML is a linked data modeling language following object-oriented and ontological principles. LinkML models are typically authored in YAML, and can be converted to other schema representation formats such as JSON or RDF.\n\nThis repo holds the tools for generating and working with LinkML. For the LinkML schema (metamodel), please see https://github.com/linkml/linkml-model\n\nThe complete documentation for LinkML can be found here:\n\n - [linkml.io/linkml](https://linkml.io/linkml)\n',
    'author': 'Chris Mungall',
    'author_email': 'cjmungall@lbl.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://linkml.io/linkml/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.6,<4.0.0',
}


setup(**setup_kwargs)
