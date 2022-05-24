# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['linkml_runtime',
 'linkml_runtime.dumpers',
 'linkml_runtime.linkml_model',
 'linkml_runtime.loaders',
 'linkml_runtime.utils']

package_data = \
{'': ['*'],
 'linkml_runtime.linkml_model': ['graphql/*',
                                 'json/*',
                                 'jsonld/*',
                                 'jsonschema/*',
                                 'model/*',
                                 'model/docs/*',
                                 'model/schema/*',
                                 'owl/*',
                                 'rdf/*',
                                 'shex/*']}

install_requires = \
['click',
 'deprecated',
 'hbreader',
 'json-flattener>=0.1.9',
 'jsonasobj2>=1.0.4,<2.0.0',
 'jsonschema>=3.2.0',
 'prefixcommons',
 'pyyaml',
 'rdflib>=6.0.0',
 'requests']

entry_points = \
{'console_scripts': ['comparefiles = linkml_runtime.utils.comparefiles:cli']}

setup_kwargs = {
    'name': 'linkml-runtime',
    'version': '1.2.15',
    'description': 'Runtime environment for LinkML, the Linked open data modeling language',
    'long_description': '# linkml-runtime\n[![Pyversions](https://img.shields.io/pypi/pyversions/linkml-runtime.svg)](https://pypi.python.org/pypi/linkml-runtime)\n![](https://github.com/linkml/linkml-runtime/workflows/Build/badge.svg)\n[![badge](https://img.shields.io/badge/launch-binder-579ACA.svg)](https://mybinder.org/v2/gh/linkml/linkml-runtime/main?filepath=notebooks)\n[![PyPi](https://img.shields.io/pypi/v/linkml-runtime.svg)](https://pypi.python.org/pypi/linkml)\n[![PyPIDownloadsTotal](https://pepy.tech/badge/linkml-runtime)](https://pepy.tech/project/linkml-runtime)\n[![PyPIDownloadsMonth](https://img.shields.io/pypi/dm/linkml-runtime?logo=PyPI&color=blue)](https://pypi.org/project/linkml-runtime)\n[![codecov](https://codecov.io/gh/linkml/linkml-runtime/branch/main/graph/badge.svg?token=FOBHNSK5WG)](https://codecov.io/gh/linkml/linkml-runtime)\n\nRuntime support for linkml generated models\n\n## About\n\nThis python library provides runtime support for [LinkML](https://linkml.io/linkml/) datamodels.\n\nSee the [LinkML repo](https://github.com/linkml/linkml) for the [Python Dataclass Generator](https://linkml.io/linkml/generators/python.html) which will convert a schema into a Python object model. That model will have dependencies on functionality in this library.\n\nThe library also provides\n\n* loaders: for loading from external formats such as json, yaml, rdf, tsv into LinkML instances\n* dumpers: the reverse operation\n\nSee [working with data](https://linkml.io/linkml/data/index.html) in the documentation for more details\n\nThis repository also contains the Python dataclass representation of the [LinkML metamodel](https://github.com/linkml/linkml-model), and various utility functions that are useful for working with LinkML data and schemas.\n\nIt also includes the [SchemaView](https://linkml.io/linkml/developers/manipulating-schemas.html) class for working with LinkML schemas\n\n## Notebooks\n\nSee the [notebooks](https://github.com/linkml/linkml-runtime/tree/main/notebooks) folder for examples\n',
    'author': 'Chris Mungall',
    'author_email': 'cjmungall@lbl.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/linkml/linkml-runtime',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
