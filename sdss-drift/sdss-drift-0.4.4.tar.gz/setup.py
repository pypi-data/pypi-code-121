# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['drift']

package_data = \
{'': ['*']}

install_requires = \
['pymodbus>=2.5.0,<3.0.0', 'sdsstools>=0.4.1']

setup_kwargs = {
    'name': 'sdss-drift',
    'version': '0.4.4',
    'description': 'Modbus PLC control library',
    'long_description': "# SDSS-V Modbus PCL library\n\n![Versions](https://img.shields.io/badge/python->3.7-blue)\n[![Documentation Status](https://readthedocs.org/projects/sdss-drift/badge/?version=latest)](https://sdss-drift.readthedocs.io/en/latest/?badge=latest)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n![Build](https://img.shields.io/github/workflow/status/sdss/drift/Test)\n[![codecov](https://codecov.io/gh/sdss/drift/branch/master/graph/badge.svg)](https://codecov.io/gh/sdss/drift)\n\nThis library provides an asynchronous interface with modbus devices over a TCP ethernet controller (such as [this one](https://www.wago.com/us/controllers-bus-couplers-i-o/controller-modbus-tcp/p/750-862)) and control of the connected I/O modules. The code is a relatively thin wrapper around [Pymodbus](http://riptideio.github.io/pymodbus/) with the main feature being that it's possible to define a PLC controller and a complete set of modules as a YAML configuration file which can then be loaded. It also provides convenience methods to read and write to the I/O modules and to convert the read values to physical units.\n\nThis code is mostly intended to interface with the SDSS-V [FPS](https://www.sdss.org/future/technology/) electronic boxes but is probably general enough for other uses. It's originally based on Rick Pogge's [WAGO code](https://github.com/sdss/FPS/tree/master/WAGO).\n\n## Installation\n\nTo install, run\n\n```console\npip install sdss-drift\n```\n\nTo install from source, git clone or download the code, navigate to the root of the downloaded directory, and do\n\n```console\npip install .\n```\n\n`sdss-drift` uses [Poetry](https://poetry.eustace.io/) for development. To install it in development mode do\n\n```console\npoetry install -E docs\n```\n\n## Documentation\n\nRefer to the Read the Docs [documentation](https://sdss-drift.readthedocs.io/en/latest) for more details.\n",
    'author': 'José Sánchez-Gallego',
    'author_email': 'gallegoj@uw.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/sdss/drift',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
