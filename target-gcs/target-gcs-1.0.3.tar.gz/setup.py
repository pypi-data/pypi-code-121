# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['target_gcs', 'target_gcs.tests']

package_data = \
{'': ['*']}

install_requires = \
['google-api-python-client>=2.49.0,<3.0.0',
 'google-cloud-storage>=2.3.0,<3.0.0',
 'orjson>=3.6.8,<4.0.0',
 'pytest-watch>=4.2.0,<5.0.0',
 'requests>=2.25.1,<3.0.0',
 'singer-sdk>=0.5.0,<0.6.0',
 'smart-open[gcs]>=6.0.0,<7.0.0']

entry_points = \
{'console_scripts': ['target-gcs = target_gcs.target:TargetGCS.cli']}

setup_kwargs = {
    'name': 'target-gcs',
    'version': '1.0.3',
    'description': '`target-gcs` is a Singer target for GCS, built with the Meltano SDK for Singer Targets.',
    'long_description': None,
    'author': 'Datateer Ops',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
