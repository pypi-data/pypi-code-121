# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yellowbox', 'yellowbox.extras', 'yellowbox.extras.webserver']

package_data = \
{'': ['*']}

install_requires = \
['Deprecated>=1.2.13,<2.0.0',
 'docker>=4.2.0,<6.0.0',
 'requests',
 'yaspin>=1.0.0,<2.0.0']

extras_require = \
{'azure': ['azure-storage-blob', 'cffi>=1.14.0,<2.0.0'],
 'dev': ['redis>=3.3.0',
         'pika',
         'kafka-python',
         'azure-storage-blob',
         'cffi>=1.14.0,<2.0.0',
         'sqlalchemy>=1.3.0,<2.0.0',
         'psycopg2>=2.8.6,<3.0.0',
         'simple_websocket_server',
         'starlette>=0.9.0',
         'uvicorn>=0.13.0',
         'websockets',
         'hvac',
         'pyodbc>=4.0.32,<5.0.0',
         'SQLAlchemy-Utils>=0.38.2,<0.39.0'],
 'kafka': ['kafka-python'],
 'mssql': ['sqlalchemy>=1.3.0,<2.0.0', 'SQLAlchemy-Utils>=0.38.2,<0.39.0'],
 'postgresql': ['sqlalchemy>=1.3.0,<2.0.0',
                'psycopg2>=2.8.6,<3.0.0',
                'SQLAlchemy-Utils>=0.38.2,<0.39.0'],
 'rabbit': ['pika'],
 'redis': ['redis>=3.3.0'],
 'vault': ['hvac'],
 'webserver': ['starlette>=0.9.0', 'uvicorn>=0.13.0', 'websockets'],
 'websocket': ['simple_websocket_server']}

entry_points = \
{'pytest11': ['yellowbox = yellowbox._pytest']}

setup_kwargs = {
    'name': 'yellowbox',
    'version': '0.7.2',
    'description': '',
    'long_description': '# Yellowbox\n![Test YellowBox](https://github.com/biocatchltd/yellowbox/workflows/Test%20YellowBox/badge.svg?branch=master)\n[![Coverage](https://codecov.io/github/biocatchltd/yellowbox/coverage.svg?branch=master)](https://codecov.io/github/biocatchltd/yellowbox?branch=master)\n\n\nYellowbox makes it easy to run docker containers as part of black box tests.\n\n**Documentation:** https://yellowbox.readthedocs.io/\n\n---\n## Examples\nSay you want to run a blackbox test on a service that depends on a redis server.\n\n```python\nfrom yellowbox.clients import docker_client\nfrom yellowbox.extras import RedisService\n\n\ndef test_black_box():\n  with docker_client() as docker_client, RedisService.run(docker_client) as redis:\n    redis_port = redis.client_port()  # this the host port the redis\n    ...  # run your black box test here\n  # yellowbox will automatically close the service when exiting the scope\n\n\ndef test_black_box_with_initial_data():\n  # you can use the service\'s built-in utility functions to\n  # easily interoperate the service\n  with docker_client() as docker_client,\n          RedisService.run(docker_client) as redis,\n          redis.client() as client:\n    client.set("foo", "bar")\n  ...\n```\n\n## License\nYellowbox is registered under the MIT public license\n',
    'author': 'biocatch ltd',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/biocatchltd/yellowbox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
