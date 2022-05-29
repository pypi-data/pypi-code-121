# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['salt_nornir',
 'salt_nornir.modules',
 'salt_nornir.proxy',
 'salt_nornir.runners',
 'salt_nornir.states']

package_data = \
{'': ['*']}

install_requires = \
['nornir==3.2.0', 'nornir_salt>=0.11.0,<0.12.0', 'pydantic>=1.9.0,<1.10.0']

extras_require = \
{'docs': ['readthedocs-sphinx-search==0.1.1',
          'Sphinx==4.3.0',
          'sphinx_rtd_theme==1.0.0',
          'sphinxcontrib-applehelp==1.0.1',
          'sphinxcontrib-devhelp==1.0.1',
          'sphinxcontrib-htmlhelp==2.0.0',
          'sphinxcontrib-jsmath==1.0.1',
          'sphinxcontrib-napoleon==0.7',
          'sphinxcontrib-qthelp==1.0.2',
          'sphinxcontrib-serializinghtml==1.1.5',
          'sphinxcontrib-spelling==7.2.1'],
 'prodmax': ['cerberus==1.3.4',
             'jmespath==0.10.0',
             'napalm==3.3.1',
             'ncclient==0.6.9',
             'netmiko==3.4.0',
             'nornir-napalm==0.1.2',
             'nornir-netmiko==0.1.2',
             'nornir-scrapli==2021.7.30',
             'ntc-templates>=1.7.0,<2.0.0',
             'paramiko==2.9.2',
             'pygnmi==0.6.8',
             'pyyaml==6.0',
             'requests==2.27.1',
             'rich==11.2.0',
             'scrapli==2021.7.30',
             'scrapli-community==2021.7.30',
             'scrapli-netconf==2022.1.30a1',
             'tabulate==0.8.9',
             'ttp==0.8.4',
             'ttp-templates>=0.1.0,<0.2.0',
             'xmltodict==0.12.0'],
 'prodmax:sys_platform != "win32"': ['genie==22.1', 'pyats==22.1'],
 'prodmin': ['ncclient==0.6.9',
             'netmiko==3.4.0',
             'nornir-netmiko==0.1.2',
             'paramiko==2.9.2',
             'requests==2.27.1',
             'rich==11.2.0',
             'tabulate==0.8.9',
             'ttp==0.8.4',
             'ttp-templates>=0.1.0,<0.2.0',
             'xmltodict==0.12.0']}

entry_points = \
{'salt.loader': ['module_dirs = salt_nornir.loader:module_dirs',
                 'proxy_dirs = salt_nornir.loader:proxy_dirs',
                 'runner_dirs = salt_nornir.loader:runner_dirs',
                 'states_dirs = salt_nornir.loader:states_dirs']}

setup_kwargs = {
    'name': 'salt-nornir',
    'version': '0.11.0',
    'description': 'Salt-Nornir Proxy Minion SaltStack Modules',
    'long_description': '[![Downloads][pepy-downloads-badge]][pepy-downloads-link]\n[![PyPI][pypi-latest-release-badge]][pypi-latest-release-link]\n[![PyPI versions][pypi-versions-badge]][pypi-versions-link]\n[![GitHub Discussion][github-discussions-badge]][github-discussions-link]\n[![Code style: black][black-badge]][black-link]\n[![Documentation status][readthedocs-badge]][readthedocs-link]\n\n![logo][logo]\n\n# Salt Nornir\n\nRepository to store Nornir based SaltStack modules:\n\n- salt-nornir proxy minion module\n- salt-nornir execution module\n- salt-nornir state module\n- salt-nornir runner module\n\nNornir Proxy Minion helps to manage network devices at scale, reference\n[documentation](https://salt-nornir.readthedocs.io/en/latest/index.html)\nfor details.\n\n# Architecture\n\nPython and Plugins.\n\n![architecture][architecture]\n\nNornir Proxy acts as a bridge between SaltStack and a wide set of network automation libraries.\n\n# Advantages\n\nSome notable benefits:\n\n- Well tested - overall 500 tests for `salt-nornir` and `nornir-salt` packages combined as of release 0.10.0\n- Brings together SaltStack and a wealth of open-source libraries - Nornir, Netmiko, NAPALM, Scrapli, Scrapli-Netconf, Ncclient, Genie&PyATS (free, not open-source), PyGNMI, NTC-Templates, TTP, Jmespath, lxml, xmltodict, requests\n- Capable of addressing overwhelming set of use cases from simple data retrieval and parsing to infrastructure provisioning, testing, orchestration and self-healing\n- Python is a first class citizen, need something special - write your own plugins, modules, scripts, codify your work flows\n- Integrate anything with anything, all you can do via CLI you can do via SaltStack and Nornir Python API or SaltStack REST API\n\n# Communication and discussion\n\nNetwork To Code [salt-nornir Slack Channel](https://app.slack.com/client/T09LQ7E9E/C02MPR34DGF)\n\nOpen an [issue](https://github.com/dmulyalin/salt-nornir/issues)\n\nStart a [discussion](https://github.com/dmulyalin/salt-nornir/discussions)\n\n# Contributing\n\nIssues, bug reports and feature requests are welcomed. Feedback is a gift and we truly value it.\n\n# Authors Guidelines\n\n- if it is not in the docs it does not exist\n- if it is not tested it is broken\n- done is better than perfect\n- keep it stupid simple\n\n[logo]:                        docs/source/_images/SaltNornirLogo.png "salt nornir logo"\n[architecture]:                docs/source/_images/Nornir_proxy_minion_architecture_v2.png "salt nornir architecture"\n[pepy-downloads-badge]:        https://pepy.tech/badge/salt-nornir\n[pepy-downloads-link]:         https://pepy.tech/project/salt-nornir\n[pypi-versions-badge]:         https://img.shields.io/pypi/pyversions/salt-nornir.svg\n[pypi-versions-link]:          https://pypi.python.org/pypi/salt-nornir/\n[readthedocs-badge]:           https://readthedocs.org/projects/salt-nornir/badge/?version=latest\n[readthedocs-link]:            http://salt-nornir.readthedocs.io/?badge=latest\n[pypi-latest-release-badge]:   https://img.shields.io/pypi/v/salt-nornir.svg\n[pypi-latest-release-link]:    https://pypi.python.org/pypi/salt-nornir\n[github-discussions-link]:     https://github.com/dmulyalin/salt-nornir/discussions\n[github-discussions-badge]:    https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github\n[black-badge]:                 https://img.shields.io/badge/code%20style-black-000000.svg\n[black-link]:                  https://github.com/psf/black\n[github-tests-badge]:          https://github.com/dmulyalin/salt-nornir/actions/workflows/main.yml/badge.svg\n[github-tests-link]:           https://github.com/dmulyalin/salt-nornir/actions\n',
    'author': 'Denis Mulyalin',
    'author_email': 'd.mulyalin@gmail.com',
    'maintainer': 'Denis Mulyalin',
    'maintainer_email': 'd.mulyalin@gmail.com',
    'url': 'https://github.com/dmulyalin/salt-nornir',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.5,<3.11',
}


setup(**setup_kwargs)
