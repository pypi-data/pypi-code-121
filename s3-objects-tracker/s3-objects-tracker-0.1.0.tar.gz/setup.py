# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['s3_objects_tracker']

package_data = \
{'': ['*']}

install_requires = \
['aiobotocore>=2.3.2,<3.0.0']

setup_kwargs = {
    'name': 's3-objects-tracker',
    'version': '0.1.0',
    'description': 'Track already processed objects inside your s3 bucket.',
    'long_description': '# s3-objects-tracker\n[![Build Status](https://github.com/ErhoSen/s3-objects-tracker/actions/workflows/main.yml/badge.svg)](https://github.com/ErhoSen/s3-objects-tracker/actions)\n[![codecov](https://codecov.io/gh/ErhoSen/s3-objects-tracker/branch/master/graph/badge.svg?token=GJFOTOL84G)](https://codecov.io/gh/ErhoSen/s3-objects-tracker)\n[![pypi](https://img.shields.io/pypi/v/s3-objects-tracker.svg)](https://pypi.org/project/s3-objects-tracker/)\n[![versions](https://img.shields.io/pypi/pyversions/s3-objects-tracker.svg)](https://github.com/ErhoSen/s3-objects-tracker)\n[![license](https://img.shields.io/github/license/erhosen/s3-objects-tracker.svg)](https://github.com/ErhoSen/s3-objects-tracker/blob/master/LICENSE)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nTrack already processed objects inside your s3 bucket.\n',
    'author': 'Vladimir Vyazovetskov',
    'author_email': 'erhosen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ErhoSen/s3-objects-tracker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
