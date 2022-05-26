# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ascend',
 'ascend.auth',
 'ascend.external',
 'ascend.external.protoc_gen_swagger.options',
 'ascend.log',
 'ascend.openapi',
 'ascend.openapi.openapi.openapi_client',
 'ascend.openapi.openapi.openapi_client.api',
 'ascend.protos.api',
 'ascend.protos.ascend',
 'ascend.protos.component',
 'ascend.protos.connection',
 'ascend.protos.content_encoding',
 'ascend.protos.core',
 'ascend.protos.environment',
 'ascend.protos.expression',
 'ascend.protos.external',
 'ascend.protos.fault',
 'ascend.protos.format',
 'ascend.protos.function',
 'ascend.protos.io',
 'ascend.protos.metrics',
 'ascend.protos.operator',
 'ascend.protos.pattern',
 'ascend.protos.preview',
 'ascend.protos.resource',
 'ascend.protos.resources',
 'ascend.protos.schema',
 'ascend.protos.task',
 'ascend.protos.text',
 'ascend.protos.worker',
 'ascend.sdk',
 'ascend.sdk.drd']

package_data = \
{'': ['*'], 'ascend.sdk': ['templates/v1/*', 'templates/v2/*']}

install_requires = \
['Jinja2>=3.1.1,<4.0.0',
 'MarkupSafe==2.0.1',
 'chardet==3.0.4',
 'glog>=0.3.1,<0.4.0',
 'googleapis-common-protos>=1.52,<2.0',
 'idna==2.10',
 'networkx>=2.5,<3.0',
 'protobuf>=3.17.3,<4.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'requests>=2.25.1,<3.0.0',
 'retry>=0.9.2,<0.10.0',
 'six==1.16.0',
 'urllib3>=1.26.5,<2.0.0']

entry_points = \
{'console_scripts': ['ascend = ascend.sdk.cli:run']}

setup_kwargs = {
    'name': 'ascend-io-sdk',
    'version': '0.2.42',
    'description': 'The Ascend SDK for Python',
    'long_description': None,
    'author': 'Ascend Engineering',
    'author_email': 'support@ascend.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
