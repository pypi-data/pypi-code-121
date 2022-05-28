# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['monitoring_as_code',
 'monitoring_as_code.binds',
 'monitoring_as_code.binds.grafana',
 'monitoring_as_code.binds.grafana.client',
 'monitoring_as_code.binds.grafana.client.alert_queries',
 'monitoring_as_code.binds.grafana.handlers',
 'monitoring_as_code.binds.grafana.objects',
 'monitoring_as_code.controller',
 'monitoring_as_code.controller.states']

package_data = \
{'': ['*']}

install_requires = \
['durationpy>=0.5,<0.6',
 'loguru>=0.6.0,<0.7.0',
 'pydantic>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'retry>=0.9.2,<0.10.0']

setup_kwargs = {
    'name': 'monitoring-as-code',
    'version': '0.0.1',
    'description': 'A monitoring as code approach library',
    'long_description': None,
    'author': 'Daniil Manakovskiy',
    'author_email': 'd.manakovskiy@innopolis.university',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
