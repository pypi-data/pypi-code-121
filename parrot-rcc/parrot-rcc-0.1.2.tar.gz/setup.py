# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['parrot_rcc']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.1.3,<9.0.0',
 'pyzeebe>=3.0.4,<4.0.0',
 'uvloop>=0.16.0,<0.17.0']

entry_points = \
{'console_scripts': ['parrot-rcc = parrot_rcc.cli:main']}

setup_kwargs = {
    'name': 'parrot-rcc',
    'version': '0.1.2',
    'description': 'Zeebe external task Robot Framework RCC client',
    'long_description': '`parrot-rcc` mimics https://pypi.org/project/carrot-rcc/ for Zeebe.\n\n`parrot-rcc` is Work in progress.\n\n```\nUsage: parrot-rcc [OPTIONS] [ROBOTS]...\n\n  Zeebe external task Robot Framework RCC client\n\n  [ROBOTS] could also be passed as a space separated env RCC_ROBOTS\n\nOptions:\n  --rcc-executable TEXT\n  --rcc-controller TEXT\n  --rcc-fixed-spaces BOOLEAN\n  --rcc-telemetry BOOLEAN\n  --task-timeout-ms INTEGER\n  --task-max-jobs INTEGER\n  --zeebe-hostname TEXT\n  --zeebe-port INTEGER\n  --camunda-client-id TEXT\n  --camunda-client-secret TEXT\n  --camunda-cluster-id TEXT\n  --camunda-region TEXT\n  --log-level TEXT\n  --help                        Show this message and exit.\n```\n',
    'author': 'Asko Soukka',
    'author_email': 'asko.soukka@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/datakurre/parrot-rcc',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
