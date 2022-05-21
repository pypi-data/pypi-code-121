# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['puresnmp',
 'puresnmp.aio',
 'puresnmp.aio.api',
 'puresnmp.api',
 'puresnmp.test',
 'puresnmp.test.external_api',
 'puresnmp.test.gh-issues',
 'puresnmp.test.test',
 'puresnmp.test.x690',
 'puresnmp.x690']

package_data = \
{'': ['*'],
 'puresnmp.test': ['data/*', 'data/apiv1/*', 'data/gh-issues/*', 'data/x690/*']}

install_requires = \
['six', 't61codec>=1.0.1', 'verlib']

extras_require = \
{':python_version < "3.3"': ['ipaddress', 'mock'],
 ':python_version < "3.5"': ['typing'],
 ':python_version < "3.8"': ['importlib_metadata']}

setup_kwargs = {
    'name': 'puresnmp',
    'version': '1.11.0.post1',
    'description': 'Pure Python SNMP implementation',
    'long_description': ".. >>> Shields >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n.. image:: https://travis-ci.org/exhuma/puresnmp.svg?branch=develop\n    :target: https://travis-ci.org/exhuma/puresnmp\n\n.. image:: https://readthedocs.org/projects/puresnmp/badge/?version=latest\n    :target: http://puresnmp.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n\n.. image:: https://img.shields.io/badge/repository-github-green.svg?style=flat\n    :target: https://github.com/exhuma/puresnmp\n    :alt: Github Project\n\n.. image:: https://img.shields.io/pypi/v/puresnmp.svg\n    :alt: PyPI\n    :target: https://pypi.org/project/puresnmp/\n\n.. <<< Shields <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n----\n\n\nTL;DR\n-----\n\nJump right in with the `cookbook`_\n\n----\n\n\nQuick Info\n----------\n\nWhat\n    A pure Python implementation for Python 3.3+ of SNMP without any external\n    dependencies (neither MIBs or libsnmp).\n\nWhy\n    SNMP in itself is simple and well defined. A bit convoluted, but simple.\n    MIB parsing however complicates the code-base and is *technically* not\n    required. They add typing information and variables and give names to OIDs.\n    All existing libraries have a direct or indirect dependency on libsnmp.\n    With all the advantages and disadvantages.\n\n    The aim of this project is to focus on SNMP in itself and provide a very\n    simple API. Instead of implementing ASN.1 parsing, the SNMP related ASN.1\n    and X.690 information is hard-coded (keeping in mind that all that's\n    hard-coded is well defined).\n\n    It is of course possible to *wrap* this package in another package adding\n    MIB parsing and processing. This is, and will be however **out of the scope\n    of this project**!\n\nWhen\n    First commit: Sat Jul 23 12:01:05 2016 +0200\n\nWho\n    Michel Albert\n\n\nInstallation\n------------\n\n::\n\n    pip install puresnmp\n\n\n\nPackage Version Numbers\n-----------------------\n\nAs an important side-note, you might want to know that this project follows\n`Semantic Versioning`_.\n\nExamples\n--------\n\nSee the `cookbook`_.\n\n.. _cookbook: http://puresnmp.readthedocs.io/en/latest/cookbook/index.html\n.. _Semantic Versioning: http://semver.org/spec/v2.0.0.html\n",
    'author': 'Michel Albert',
    'author_email': 'michel@albert.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/exhuma/puresnmp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
