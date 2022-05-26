# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['serverless',
 'serverless.aws',
 'serverless.aws.alerts',
 'serverless.aws.features',
 'serverless.aws.functions',
 'serverless.aws.iam',
 'serverless.aws.resources',
 'serverless.integration',
 'serverless.service',
 'serverless.service.plugins']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'awacs>=2.1.0,<3.0.0',
 'inflection>=0.5.1,<0.6.0',
 'troposphere>=3.2,<3.3']

entry_points = \
{'console_scripts': ['slscli = serverless.cli:cli']}

setup_kwargs = {
    'name': 'serverless-builder',
    'version': '2.8.0',
    'description': 'Python interface to easily generate `serverless.yml`.',
    'long_description': '<h2 align="center">serverless-builder</h2>\n<p align="center">\n<a href="https://pypi.org/project/serverless-builder/"><img alt="PyPI" src="https://img.shields.io/pypi/v/serverless-builder"></a>\n<a href="https://pypi.org/project/serverless-builder/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/serverless-builder.svg"></a>\n<a href="https://github.com/epsylabs/serverless-builder/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/serverless-builder.svg"></a>\n</p>\n\nPython interface to easily generate [serverless.yml](https://www.serverless.com/) file.\n\nTo read more about features, visit [📜 our documentation](https://epsylabs.github.io/serverless-builder/).\n\n## Installation\n```shell\npip install serverless-builder\n```\n\n## Features\n* [plugin management](https://epsylabs.github.io/serverless-builder/plugins/) with autoconfiguration\n* [function factory](https://epsylabs.github.io/serverless-builder/usage/#lambda-functions) with some best practice hints\n* autoconfiguration of some provider specific features like AWS X-Ray\n* easy resource manipulation with [troposphere lib](https://github.com/cloudtools/troposphere) (but if you want you can use old good dict)\n* easier IAM management with predefined permission sets\n* built-in support for any serverless attributes\n* integration with [aws lambda powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/)\n\n## Example of use\n\n```python\nfrom serverless.aws.functions.event_bridge import RetryPolicy\nfrom serverless.aws.functions.http import HTTPFunction\nfrom serverless import Service\nfrom serverless.provider import AWSProvider\nfrom serverless.aws.features import XRay\nfrom serverless.aws.iam.dynamodb import DynamoDBReader\nfrom serverless.plugins import ComposedVars, PythonRequirements, Prune\n\nfrom troposphere.dynamodb import Table, AttributeDefinition, KeySchema\n\nservice = Service(\n    "service-name",\n    "some dummy service",\n    AWSProvider()\n)\nservice.plugins.add(ComposedVars())\nservice.plugins.add(Prune())\nservice.plugins.add(PythonRequirements())\n\ntable = Table(\n    "TestTable",\n    BillingMode="PAY_PER_REQUEST",\n    AttributeDefinitions=[\n        AttributeDefinition(AttributeName="name", AttributeType="S")\n    ],\n    KeySchema=[KeySchema(AttributeName="name", KeyType="HASH")]\n)\n\nservice.enable(XRay())\nservice.provider.iam.apply(DynamoDBReader(table))\n\nservice.builder.function.generic("test", "description")\nservice.builder.function.http("test", "description", "/", HTTPFunction.POST)\n\n# Multiple events with different paths and/or methods can be set up for the same handler\n# This will add the same handler to all of these: POST /, POST /alias, PUT /, PUT /alias\nservice.builder.function.http("test", "description", ["/", "/alias"], ["POST", "PUT"], handler="shared.handler")\n\n# Context with pre-defined setup\nwith service.preset(\n    layers=[{"Ref": "PythonRequirementsLambdaLayer"}],\n    handler="test.handlers.custom_handler.handle"\n) as p:\n    p.http_get("test-list", "List all tests", "/")\n    p.http_get("test-get", "Get one test", "/{test_id}")\n\nevent_bridge_function = service.builder.function.event_bridge(\n    "event_bridge_function",\n    "sample event bridge function",\n    "epsy",\n    {"source": ["saas.external"]},\n)\n\nevent_bridge_function.use_delivery_dlq(RetryPolicy(5, 300))\nevent_bridge_function.use_async_dlq()\n\nservice.resources.add(table)\n\nservice.render()\n```\n',
    'author': 'Epsy',
    'author_email': 'engineering@epsyhealth.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://epsylabs.github.io/serverless-builder/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
