# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strangeworks', 'strangeworks.rigetti']

package_data = \
{'': ['*']}

install_requires = \
['pyquil>=3.1,<3.2', 'strangeworks>=0.2.0,<0.3.0']

setup_kwargs = {
    'name': 'strangeworks-rigetti',
    'version': '0.2.10',
    'description': 'Strangeworks Rigetti SDK extension',
    'long_description': '| ⚠️    | This SDK is currently in pre-release alpha state and subject to change. To get more info or access to test features check out the [Strangeworks Backstage Pass Program](https://strangeworks.com/backstage). |\n|---------------|:------------------------|\n# Strangeworks Rigetti Extension\n\n Strangeworks Python SDK extension for Rigetti.\n\n\n \n For more information on using the SDK check out the [Strangeworks documentation](https://docs.strangeworks.com/).\n',
    'author': 'Strange Devs',
    'author_email': 'hello@strangeworks.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
