# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cozifytemp']

package_data = \
{'': ['*']}

install_requires = \
['absl-py>=1.0.0,<2.0.0',
 'cozify==0.2.33',
 'influxdb-client>=1.19.0,<2.0.0',
 'pytz>=2021.1,<2022.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['cozifytemp-sample-loop = cozifytemp.sample_loop:run',
                     'cozifytemp-single-sample = '
                     'cozifytemp.single_sample:main']}

setup_kwargs = {
    'name': 'cozifytemp',
    'version': '0.1.2',
    'description': 'Sample Cozify sensor to influxdb logger',
    'long_description': None,
    'author': 'Artanicus',
    'author_email': 'artanicus@nocturnal.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
