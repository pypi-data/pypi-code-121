# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flow',
 'flow.cli',
 'flow.cli.commands',
 'flow.cli.commands.bots',
 'flow.cli.commands.config',
 'flow.cli.commands.debug',
 'flow.cli.commands.policies',
 'flow.cli.commands.resources',
 'flow.cli.commands.services',
 'flow.cli.commands.services.click',
 'flow.cli.commands.services.hooks',
 'flow.cli.commands.tokens',
 'flow.cli.commands.users',
 'flow.cli.helpers',
 'flow.cli.helpers.login',
 'flow.cli.models',
 'flow.cli.tests',
 'flow.cli.tests.commands',
 'flow.cli.tests.commands.bots',
 'flow.cli.tests.commands.config',
 'flow.cli.tests.commands.debug',
 'flow.cli.tests.commands.resources',
 'flow.cli.tests.commands.services',
 'flow.cli.tests.commands.services.hooks',
 'flow.cli.tests.commands.tokens',
 'flow.cli.tests.commands.users',
 'flow.cli.tests.factories',
 'flow.cli.tests.helpers',
 'flow.cli.tests.helpers.iam_policies',
 'flow.cli.tests.helpers.login',
 'flow.cli.tests.models']

package_data = \
{'': ['*']}

install_requires = \
['analytics-python>=1.3.1,<2.0.0',
 'boto3>=1.16.20,<2.0.0',
 'click>=8.0.0,<9.0.0',
 'immutables>=0.14,<0.15',
 'inflection>=0.5.1,<0.6.0',
 'inquirer>=2.7.0,<3.0.0',
 'mistune<2.0.0',
 'pkce>=1.0,<2.0',
 'policy-sentry==0.9.0',
 'prompt-toolkit>=3.0.21,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pytest-factoryboy>=2.1.0,<3.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'semver>=2.13.0,<3.0.0',
 'sentry-sdk>=0.19.3,<0.20.0',
 'sym-shared-cli>=0.2.2,<0.3.0',
 'tabulate>=0.8.7,<0.9.0',
 'validators>=0.18.1,<0.19.0',
 'xattr>=0.9.7,<0.10.0']

entry_points = \
{'console_scripts': ['symflow = sym.flow.cli.symflow:symflow']}

setup_kwargs = {
    'name': 'sym-flow-cli',
    'version': '1.6.0',
    'description': "Sym's Official CLI for Implementers",
    'long_description': '# sym-flow-cli\n\nThis is the official CLI for [Sym](https://symops.com/) Implementers. Check out the docs [here](https://docs.symops.com/docs/install-sym-flow).\n',
    'author': 'SymOps, Inc.',
    'author_email': 'pypi@symops.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://symops.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
