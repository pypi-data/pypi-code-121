# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cisco_opentelemetry_specifications']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cisco-opentelemetry-specifications',
    'version': '0.0.17',
    'description': 'Cisco Opentelemetry specifications',
    'long_description': '# This is an auto generated repo for all Cisco OpenTelemetry specifications\n',
    'author': 'Cisco Epsagon Team',
    'author_email': 'support@epsagon.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/epsagon/cisco-otel-distribution-specifications',
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
