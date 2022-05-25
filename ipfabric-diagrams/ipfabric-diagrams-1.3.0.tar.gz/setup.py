# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ipfabric_diagrams',
 'ipfabric_diagrams.input_models',
 'ipfabric_diagrams.input_models.factory_defaults',
 'ipfabric_diagrams.output_models']

package_data = \
{'': ['*']}

install_requires = \
['ipfabric>=0,<1', 'pydantic>=1.8.2,<2.0.0', 'typing-extensions>=4.1.1,<5.0.0']

setup_kwargs = {
    'name': 'ipfabric-diagrams',
    'version': '1.3.0',
    'description': 'Python package for interacting with IP Fabric Diagrams',
    'long_description': "# IPFabric\n\nipfabric-diagrams is a Python module for connecting to and graphing topologies against an IP Fabric instance.\n\n[![Requirements Status](https://requires.io/github/community-fabric/python-ipfabric-diagrams/requirements.svg?branch=main)](https://requires.io/github/community-fabric/python-ipfabric-diagrams/requirements/?branch=main)\n\n## About\n\nFounded in 2015, [IP Fabric](https://ipfabric.io/) develops network infrastructure visibility and analytics solution to\nhelp enterprise network and security teams with network assurance and automation across multi-domain heterogeneous\nenvironments. From in-depth discovery, through graph visualization, to packet walks and complete network history, IP\nFabric enables to confidently replace manual tasks necessary to handle growing network complexity driven by relentless\ndigital transformation.\n\n## Installation\n\n```\npip install ipfabric-diagrams\n```\n\n## Introduction\n\nThis package is used for diagramming via the API for IP Fabric v4.3.0.  \nExamples can be located under [examples](examples/) directory.\n\n## Authentication\nPlease take a look at [python-ipfabric](https://github.com/community-fabric/python-ipfabric/blob/main/examples/basic.py) \nfor all authentication options.\n\n```python\nfrom ipfabric_diagrams import IPFDiagram\nipf = IPFDiagram(base_url='https://demo3.ipfabric.io/', token='token', verify=False, timeout=15)\n```\n\n## Development\n\nIPFabric uses poetry for the python packaging module. Install poetry globally:\n\n```\npip install poetry\n```\n\nTo install a virtual environment run the following command in the root of this directory.\n\n```\npoetry install\n```\n\nTo test and build:\n\n```\npoetry run pytest\npoetry build\n```\n\nGitHub Actions will publish and release. Make sure to tag your commits:\n\n* ci: Changes to our CI configuration files and scripts\n* docs: No changes just documentation\n* test: Added test cases\n* perf: A code change that improves performance\n* refactor: A code change that neither fixes a bug nor adds a feature\n* style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)\n* fix: a commit of the type fix patches a bug in your codebase (this correlates with PATCH in Semantic Versioning). \n* feat: a commit of the type feat introduces a new feature to the codebase (this correlates with MINOR in Semantic Versioning). \n* BREAKING CHANGE: a commit that has a footer BREAKING CHANGE:, or appends a ! after the type/scope, introduces a breaking\nAPI change (correlating with MAJOR in Semantic Versioning). A BREAKING CHANGE can be part of commits of any type.\n",
    'author': 'Justin Jeffery',
    'author_email': 'justin.jeffery@ipfabric.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/community-fabric/python-ipfabric-diagrams',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
