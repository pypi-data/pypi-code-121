# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['duffy',
 'duffy.api_models',
 'duffy.app',
 'duffy.app.controllers',
 'duffy.configuration',
 'duffy.database',
 'duffy.database.migrations',
 'duffy.database.migrations.versions',
 'duffy.database.model',
 'duffy.legacy',
 'duffy.tasks',
 'duffy.tasks.mechanisms']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6,<7',
 'SQLAlchemy[asyncio]>=1.4.25,<2.0.0',
 'alembic>=1.7.5,<2.0.0',
 'bcrypt>=3.2,<4.0',
 'celery[redis]>=5.2.1,<6.0.0',
 'click>=8.0.3,<9.0.0',
 'fastapi>=0.70',
 'uvicorn>=0.15']

extras_require = \
{'all': ['Jinja2>=3.0.3,<4.0.0',
         'ansible-runner>=2.1.1,<3.0.0',
         'asyncpg>=0.25,<0.26',
         'httpx>=0.18.2',
         'ipython>=7.29',
         'jmespath>=0.10',
         'pottery>=3,<4',
         'psycopg2>=2.9.2,<3.0.0',
         'aiodns>=3.0.0,<4.0.0'],
 'interactive': ['ipython>=7.29'],
 'legacy': ['httpx>=0.18.2'],
 'postgresql': ['asyncpg>=0.25,<0.26', 'psycopg2>=2.9.2,<3.0.0'],
 'tasks': ['Jinja2>=3.0.3,<4.0.0',
           'ansible-runner>=2.1.1,<3.0.0',
           'jmespath>=0.10',
           'pottery>=3,<4',
           'aiodns>=3.0.0,<4.0.0']}

entry_points = \
{'console_scripts': ['duffy = duffy.cli:cli']}

setup_kwargs = {
    'name': 'duffy',
    'version': '3.0.0',
    'description': 'CentOS CI provisioner',
    'long_description': "## Info\nCommunity Platform Engineering team (of Red Hat) is working on revamping this project and thus, have cleaned this repository by\n* marking other branches stale\n* Clean branch created for development\n\nto see the current deployed version of Duffy in CentOS CI Infra, check stale/master branch.\n\n\n## Duffy\nDuffy is the middle layer running ci.centos.org that manages the provisioning, maintenance and teardown / rebuild of the Nodes (physical hardware for now, VMs coming soon) that are used to run the tests in the CI Cluster.\n\n## Development\n\n### Installation\nTo install Duffy:\n1. Clone the repository and navigate into the project directory.\n   ```\n   git clone https://github.com/CentOS/duffy.git\n   cd duffy\n   ```\n2. Set up and activate a virtual environment.\n   * Using native virtual environment\n     ```\n     python3 -m venv duffyenv\n     source duffyenv/bin/activate\n     ```\n   Or\n   * Using virtualenv wrapper\n     ```\n     virtualenv duffyenv\n     source duffyenv/bin/activate\n     ```\n   Or\n   * Using Poetry virtual environment shell\n     ```\n     poetry shell\n     ```\n3. Install using Poetry\n   ```\n   poetry install\n   ```\n\n### Running Duffy server\n\n#### Viewing CLI usage\n\n```\nduffy --help\n```\n\n```\nUsage: duffy [OPTIONS]\n\n  Duffy is the middle layer running ci.centos.org that manages the\n  provisioning, maintenance and teardown / rebuild of the Nodes (physical\n  hardware for now, VMs coming soon) that are used to run the tests in the CI\n  Cluster.\n\nOptions:\n  -p, --portnumb INTEGER          Set the port value [0-65536]\n  -6, --ipv6                      Start the server on an IPv6 address\n  -4, --ipv4                      Start the server on an IPv4 address\n  -l, --loglevel [critical|error|warning|info|debug|trace]\n                                  Set the log level\n  --version                       Show the version and exit.\n  --help                          Show this message and exit.\n```\n\n#### Starting the server at port 8080 using IP version 4 and setting the log level to `trace`\n\n```\nduffy -p 8000 -4 -l trace\n```\n\n```\n * Starting Duffy...\n * Port number : 8000\n * IP version  : 4\n * Log level   : trace\nINFO:     Started server process [104283]\nINFO:     Waiting for application startup.\nTRACE:    ASGI [1] Started scope={'type': 'lifespan', 'asgi': {'version': '3.0', 'spec_version': '2.0'}}\nTRACE:    ASGI [1] Receive {'type': 'lifespan.startup'}\nTRACE:    ASGI [1] Send {'type': 'lifespan.startup.complete'}\nINFO:     Application startup complete.\nINFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)\n```\n\nExit out of the server using `Ctrl` + `C`\n",
    'author': 'Nils Philippsen',
    'author_email': 'nils@redhat.com',
    'maintainer': 'Nils Philippsen',
    'maintainer_email': 'nils@redhat.com',
    'url': 'https://github.com/CentOS/duffy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
