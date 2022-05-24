# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jetpack',
 'jetpack.cmd',
 'jetpack.config',
 'jetpack.core',
 'jetpack.errors',
 'jetpack.proto.runtime.v1alpha1',
 'jetpack.runtime',
 'jetpack.util',
 'jetpack.util.network']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'deprecation>=2.1.0,<3.0.0',
 'grpcio>=1.43.0,<2.0.0',
 'jsonpickle>=2.0.0,<3.0.0',
 'pdoc3>=0.10.0,<0.11.0',
 'protobuf>=3.17.0,<4.0.0',
 'schedule>=1.1.0,<2.0.0',
 'tblib>=1.7.0,<2.0.0']

entry_points = \
{'console_scripts': ['jetpack-sdk = jetpack:run']}

setup_kwargs = {
    'name': 'jetpack-io',
    'version': '0.5.1.dev202205241653428252',
    'description': 'Python SDK for Jetpack.io',
    'long_description': '### Jetpack SDK\n',
    'author': 'jetpack.io',
    'author_email': 'hello@jetpack.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.jetpack.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
