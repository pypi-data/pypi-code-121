# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['promail_template',
 'promail_template.templates',
 'promail_template.templates.body',
 'promail_template.templates.footer',
 'promail_template.templates.full',
 'promail_template.templates.full.hello_world',
 'promail_template.templates.header',
 'promail_template.utilities']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'click>=8.1.3,<9.0.0',
 'genson>=1.2.2,<2.0.0',
 'jsonschema>=4.5.1,<5.0.0',
 'mjml>=0.7.0,<0.8.0',
 'nox>=2022.1.7,<2023.0.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['promail-template = promail_template.console:main']}

setup_kwargs = {
    'name': 'promail-template',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Antoine Wood',
    'author_email': 'antoinewood@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
