# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ipfabric_httpx_auth']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.4.0,<3.0.0', 'httpx>=0.23.0,<0.24.0']

setup_kwargs = {
    'name': 'ipfabric-httpx-auth',
    'version': '1.0.1',
    'description': 'Authentication plugin for IP Fabric',
    'long_description': '# ipfabric_http_auth\n\nIPFabric is a Python module for connecting to and communicating against an IP Fabric instance.\n\n[![Requirements Status](https://requires.io/github/community-fabric/ipfabric_httpx_auth/requirements.svg?branch=main)](https://requires.io/github/community-fabric/ipfabric_httpx_auth/requirements/?branch=main)\n\n## About\n\nFounded in 2015, [IP Fabric](https://ipfabric.io/) develops network infrastructure visibility and analytics solution to\nhelp enterprise network and security teams with network assurance and automation across multi-domain heterogeneous\nenvironments. From in-depth discovery, through graph visualization, to packet walks and complete network history, IP\nFabric enables to confidently replace manual tasks necessary to handle growing network complexity driven by relentless\ndigital transformation.\n\n## Installation\n\n```\npip install ipfabric_httpx_auth\n```\n\n## Development\n\nIPFabric uses poetry for the python packaging module. Install poetry globally:\n\n```\npip install poetry\n```\n\nTo install a virtual environment run the following command in the root of this directory.\n\n```\npoetry install\n```\n\nTo test and build:\n\n```\npoetry run pytest\npoetry build\n```\n\nGitHub Actions will publish and release. Make sure to tag your commits:\n\n* ci: Changes to our CI configuration files and scripts\n* docs: No changes just documentation\n* test: Added test cases\n* perf: A code change that improves performance\n* refactor: A code change that neither fixes a bug nor adds a feature\n* style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)\n* fix: a commit of the type fix patches a bug in your codebase (this correlates with PATCH in Semantic Versioning).\n* feat: a commit of the type feat introduces a new feature to the codebase (this correlates with MINOR in Semantic Versioning).\n* BREAKING CHANGE: a commit that has a footer BREAKING CHANGE:, or appends a ! after the type/scope, introduces a breaking\n  API change (correlating with MAJOR in Semantic Versioning). A BREAKING CHANGE can be part of commits of any type.\n',
    'author': 'Justin Jeffery',
    'author_email': 'justin.jeffery@ipfabric.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/community-fabric/ipfabric_httpx_auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
