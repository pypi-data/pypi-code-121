# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['leapcli', 'leapcli.mapping']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0',
 'code-loader==0.2.22',
 'docopt>=0.6.2,<0.7.0',
 'leap-model-parser==0.1.3',
 'luddite>=1.0.2,<2.0.0',
 'prettytable>=3.2.0,<4.0.0',
 'python-json-logger>=2.0.2,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'semver>=2.13.0,<3.0.0',
 'tensorleap-openapi-client==1.1.13',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['leap = cli:__main__']}

setup_kwargs = {
    'name': 'leapcli',
    'version': '0.2.27',
    'description': 'Tensorleap CLI',
    'long_description': None,
    'author': 'Assaf Lavie',
    'author_email': 'assaf.lavie@tensorleap.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tensorleap/cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
