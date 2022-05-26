# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pdme', 'pdme.inputs', 'pdme.measurement', 'pdme.model', 'pdme.util']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.3,<2.0.0', 'scipy>=1.8,<1.9']

setup_kwargs = {
    'name': 'pdme',
    'version': '0.8.4',
    'description': 'Python dipole model evaluator',
    'long_description': '# pdme - the python dipole model evaluator\n\n[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-green.svg?style=flat-square)](https://conventionalcommits.org)\n[![PyPI](https://img.shields.io/pypi/v/pdme?style=flat-square)](https://pypi.org/project/pdme/)\n[![Jenkins](https://img.shields.io/jenkins/build?jobUrl=https%3A%2F%2Fjenkins.deepak.science%2Fjob%2Fgitea-physics%2Fjob%2Fpdme%2Fjob%2Fmaster&style=flat-square)](https://jenkins.deepak.science/job/gitea-physics/job/pdme/job/master/)\n![Jenkins tests](https://img.shields.io/jenkins/tests?compact_message&jobUrl=https%3A%2F%2Fjenkins.deepak.science%2Fjob%2Fgitea-physics%2Fjob%2Fpdme%2Fjob%2Fmaster%2F&style=flat-square)\n![Jenkins Coverage](https://img.shields.io/jenkins/coverage/cobertura?jobUrl=https%3A%2F%2Fjenkins.deepak.science%2Fjob%2Fgitea-physics%2Fjob%2Fpdme%2Fjob%2Fmaster%2F&style=flat-square)\n![Maintenance](https://img.shields.io/maintenance/yes/2022?style=flat-square)\n\nThis repo has library code for evaluating dipole models.\n\n## Getting started\n\n`poetry install` to start locally\n\nCommit using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), and when commits are on master, release with `doo release`.\n',
    'author': 'Deepak',
    'author_email': 'dmallubhotla+github@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
