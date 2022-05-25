# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['layer',
 'layer.cache',
 'layer.clients',
 'layer.config',
 'layer.contracts',
 'layer.decorators',
 'layer.exceptions',
 'layer.flavors',
 'layer.logged_data',
 'layer.projects',
 'layer.tracker',
 'layer.training',
 'layer.training.runtime',
 'layer.utils',
 'layer.utils.grpc']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.3',
 'Pillow>=9.1.0',
 'aiohttp>=3.7.3,<3.8.0',
 'boto3>=1.16.24',
 'cloudpickle>=2.0.0',
 'cryptography>=3.4.7',
 'docker>=4,<5',
 'grpcio-tools==1.45.0',
 'grpcio==1.45.0',
 'humanize>=3.11.0',
 'idna<3',
 'jsonschema==3.1.1',
 'layer-api==0.9.360101',
 'mlflow>=1.25.0',
 'networkx>=2.5',
 'packaging<=21.0',
 'pandas==1.3.5',
 'polling>=0.3.1',
 'prompt_toolkit>=3.0.8',
 'protobuf>=3.12.0',
 'pyarrow==7.0.0',
 'pyjwt>=1.7.1,<2.0.0',
 'rich>=11',
 'transformers',
 'validate-email==1.3',
 'wrapt>=1.13.3',
 'yarl>=1.6.3']

extras_require = \
{':python_version < "3.8"': ['pickle5>=0.0.11,<0.1.0']}

setup_kwargs = {
    'name': 'layer',
    'version': '0.10.2381661659',
    'description': 'Layer AI SDK',
    'long_description': '<!---\nCopyright 2022 Layer. All rights reserved.\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n    http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n-->\n\n<p align="center">\n    <br>\n    <a href="https://layer.ai">\n        <img src="https://app.layer.ai/assets/logo.svg" width="200" alt="Layer"/>\n    </a>\n    <br>\n<p>\n<p align="center">\n    <a href="https://github.com/layerai/sdk/blob/main/LICENSE">\n        <img alt="License" src="https://img.shields.io/github/license/layerai/sdk.svg?color=blue">\n    </a>\n    <a href="https://docs.app.layer.ai">\n        <img alt="Documentation" src="https://img.shields.io/badge/docs-online-success">\n    </a>\n    <a href="https://github.com/layerai/sdk/actions/workflows/check.yml">\n        <img alt="Build" src="https://img.shields.io/github/workflow/status/layerai/sdk/Check">\n    </a>\n    <a href="https://pypi.python.org/pypi/layer">\n        <img alt="PyPI" src="https://img.shields.io/pypi/v/layer.svg">\n    </a>\n    <a href="https://github.com/layer/sdk/blob/main/CODE_OF_CONDUCT.md">\n        <img alt="Contributor Covenant" src="https://img.shields.io/badge/contributor%20covenant-v2.1%20adopted-blueviolet.svg">\n    </a>\n</p>\n\n# Layer\n\nLayer helps you create production-grade ML pipelines with a seamless local↔cloud transition while enabling collaboration with semantic versioning, extensive artifact logging and dynamic reporting.\n\n[Start for Free!](https://app.layer.ai)\n\n## Getting Started\n\nThe simplest way to get started with Layer is to go through the [quickstart guide](https://docs.app.layer.ai/docs/getting-started).\n',
    'author': 'Layer',
    'author_email': 'info@layer.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
