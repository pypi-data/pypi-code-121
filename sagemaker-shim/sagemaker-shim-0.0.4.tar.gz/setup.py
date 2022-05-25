# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sagemaker_shim']

package_data = \
{'': ['*']}

install_requires = \
['boto3', 'click', 'fastapi', 'uvicorn[standard]']

entry_points = \
{'console_scripts': ['sagemaker-shim = sagemaker_shim.cli:cli']}

setup_kwargs = {
    'name': 'sagemaker-shim',
    'version': '0.0.4',
    'description': 'Adapts algorithms that implement the Grand Challenge inference API for running in SageMaker',
    'long_description': '# SageMaker Shim for Grand Challenge\n\n[![CI](https://github.com/jmsmkn/sagemaker-shim/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/jmsmkn/sagemaker-shim/actions/workflows/ci.yml?query=branch%3Amain)\n[![PyPI](https://img.shields.io/pypi/v/sagemaker-shim)](https://pypi.org/project/sagemaker-shim/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sagemaker-shim)](https://pypi.org/project/sagemaker-shim/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nThis repo contains a library that adapts algorithms that implement the Grand Challenge inference API for running in SageMaker.\n',
    'author': 'James Meakin',
    'author_email': '12661555+jmsmkn@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DIAGNijmegen/rse-sagemaker-shim',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
