# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['servicefoundry',
 'servicefoundry.cli',
 'servicefoundry.cli.commands',
 'servicefoundry.core',
 'servicefoundry.core.notebook',
 'servicefoundry.core.runner',
 'servicefoundry.internal',
 'servicefoundry.internal.clients',
 'servicefoundry.internal.deploy',
 'servicefoundry.internal.interceptor',
 'servicefoundry.internal.lib',
 'servicefoundry.internal.model',
 'servicefoundry.internal.package',
 'servicefoundry.internal.parser',
 'servicefoundry.internal.template',
 'servicefoundry.service',
 'servicefoundry.service.fastapi']

package_data = \
{'': ['*'], 'servicefoundry.internal': ['schema/*']}

install_requires = \
['Mako>=1.1.6,<2.0.0',
 'PyJWT>=2.3.0,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'click>=8.0.4,<9.0.0',
 'importlib-metadata>=4.2,<5.0',
 'importlib-resources>=5.2.0,<6.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'mistune>=0.8.4,<0.9.0',
 'pygments>=2.12.0,<3.0.0',
 'python-socketio[client]>=5.5.2,<6.0.0',
 'questionary>=1.10.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich-click>=1.2.1,<2.0.0',
 'rich>=12.0.0,<13.0.0']

entry_points = \
{'console_scripts': ['servicefoundry = servicefoundry.cli.__main__:main',
                     'sfy = servicefoundry.cli.__main__:main']}

setup_kwargs = {
    'name': 'servicefoundry',
    'version': '0.1.28',
    'description': 'Generate deployed services from code',
    'long_description': "# ServiceFoundry\n\nServiceFoundry is a client library that allows you to containerize and deploy your Machine Learning model (or other\nservices) to a managed Kubernetes Cluster. This also generates a Grafana cluster with complete visibility of your\nService Health, System Logs, and Kubernetes Workspace.\n\nIt is available both as a command-line-interface and via APIs that allow you to deploy directly from your Jupyter\nNotebook.\n\nYou can access the health of your service, monitoring links and deployed endpoints by logging on to TrueFoundry's\ndashboard.\n\n# Installation\n\n```\npip install -U servicefoundry\n```\n\n# Documentation\n\nhttps://docs.truefoundry.com/servicefoundry/\n",
    'author': 'Abhishek Choudhary',
    'author_email': 'abhichoudhary06@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/innoavator/servicefoundry',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
