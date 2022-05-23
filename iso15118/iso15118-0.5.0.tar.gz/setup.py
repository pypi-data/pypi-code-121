# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iso15118',
 'iso15118.evcc',
 'iso15118.evcc.controller',
 'iso15118.evcc.states',
 'iso15118.evcc.transport',
 'iso15118.secc',
 'iso15118.secc.controller',
 'iso15118.secc.states',
 'iso15118.secc.transport',
 'iso15118.shared',
 'iso15118.shared.logging',
 'iso15118.shared.messages',
 'iso15118.shared.messages.din_spec',
 'iso15118.shared.messages.iso15118_2',
 'iso15118.shared.messages.iso15118_20',
 'iso15118.shared.schemas',
 'iso15118.shared.schemas.din_spec',
 'iso15118.shared.schemas.iso15118_2',
 'iso15118.shared.schemas.iso15118_20']

package_data = \
{'': ['*'], 'iso15118.shared': ['examples/*', 'pki/*', 'pki/configs/*']}

install_requires = \
['cryptography==3.4.6',
 'environs>=9.5.0,<10.0.0',
 'psutil>=5.9.0,<6.0.0',
 'py4j>=0.10.9,<0.11.0',
 'pydantic>=1.9.0,<2.0.0']

entry_points = \
{'console_scripts': ['iso15118 = iso15118.secc.main:run']}

setup_kwargs = {
    'name': 'iso15118',
    'version': '0.5.0',
    'description': 'Implementation of DIN SPEC 70121, ISO 15118-2 and -20 specs for SECC',
    'long_description': None,
    'author': 'André Duarte',
    'author_email': 'andre@switch-ev.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
