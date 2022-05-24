# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['backends',
 'backends.postgresql',
 'django_tenants',
 'django_tenants.backends',
 'django_tenants.backends.postgresql',
 'django_tenants.files',
 'django_tenants.management',
 'django_tenants.management.commands.ignore',
 'django_tenants.middleware',
 'django_tenants.migrations',
 'django_tenants.staticfiles',
 'django_tenants.template',
 'django_tenants.template.loaders',
 'django_tenants.templatetags',
 'django_tenants.test',
 'django_tenants.tests',
 'django_tenants.tests.files',
 'django_tenants.tests.staticfiles',
 'django_tenants.tests.template',
 'django_tenants.tests.template.loaders',
 'files',
 'loaders',
 'management',
 'management.commands.ignore',
 'middleware',
 'postgresql',
 'staticfiles',
 'template',
 'template.loaders',
 'templatetags',
 'test',
 'tests',
 'tests.files',
 'tests.staticfiles',
 'tests.template',
 'tests.template.loaders']

package_data = \
{'': ['*'],
 'django_tenants': ['templates/admin/*',
                    'templates/admin/django_tenants/tenant/*']}

install_requires = \
['Django>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'picatron-tenant',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Safa Ariman',
    'author_email': 'safa@ariman.gen.tr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
