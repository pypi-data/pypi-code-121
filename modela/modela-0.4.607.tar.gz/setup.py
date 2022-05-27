# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modela',
 'modela.data',
 'modela.inference',
 'modela.infra',
 'modela.team',
 'modela.training']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.44.0,<2.0.0',
 'kubernetes>=21.7.0,<22.0.0',
 'modelaapi==0.4.607',
 'protobuf>=3.19.3,<4.0.0']

setup_kwargs = {
    'name': 'modela',
    'version': '0.4.607',
    'description': 'python client sdk for the modela auto ml system.',
    'long_description': '## What is Modela?\n\nModela is a Kubernetes-based automatic machine learning platform that enables you with an expansive API for machine\nlearning. The system implements Kubernetes custom resources for declaratively managing data, training, inference, and \ninfrastructure objects. The Modela control plane manages these resources to provide fully distributed and automated machine learning. \n\n\nFor a complete documentation of the API, check out the [documentation](https://www.modela.ai/docs/docs).\n\n## Install Modela\n\nModela can be installed through the Modela CLI, or through Helm Charts. For a complete installation procedure, please \nrefer to the installation procedure on the [documentation](https://www.modela.ai/docs/docs/install).\n\n## Using the SDK\n\nThe Modela API is implemented by [Modela](https://modela.ai), which can be installed on \nany Kubernetes cluster for free. You can access the API by connecting to the API gateway service hosted by your installation.\n\n',
    'author': 'liam',
    'author_email': 'liam@metaprov.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/metaprov/modela-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
