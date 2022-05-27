# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['teapod', 'teapod.scripts']

package_data = \
{'': ['*']}

install_requires = \
['pytoml', 'resworb', 'rich']

entry_points = \
{'console_scripts': ['information = teapod.scripts.information:main',
                     'org-import = teapod.scripts.org_import:main',
                     'pip-update-all = teapod.scripts.pip_update_all:main',
                     'poetry-add-latest = '
                     'teapod.scripts.poetry_add_latest:main',
                     'poetry-export-requirements = '
                     'teapod.scripts.poetry_export_requirements:main',
                     'surge-to-ss = teapod.scripts.surge_to_ss:main']}

setup_kwargs = {
    'name': 'teapod',
    'version': '0.3.8',
    'description': 'Teapod.',
    'long_description': None,
    'author': 'Yevgnen Koh',
    'author_email': 'wherejoystarts@gmail.com',
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
