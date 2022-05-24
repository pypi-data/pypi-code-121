# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stepview']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.21.42,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'rich>=12.0.1,<13.0.0',
 'textual>=0.1.17,<0.2.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['stepview = stepview.entrypoint:run']}

setup_kwargs = {
    'name': 'stepview',
    'version': '0.4.2',
    'description': '1 global view of all your stepfunctions statemachines',
    'long_description': None,
    'author': 'vincent',
    'author_email': 'vclaes1986@gmail.com',
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
