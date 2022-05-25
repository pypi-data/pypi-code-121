# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deeco',
 'deeco.plugins',
 'mission_control',
 'mission_control.common_descriptors',
 'mission_control.coordination',
 'mission_control.data_model',
 'mission_control.deeco_integration',
 'mission_control.deeco_integration.plugins',
 'mission_control.deeco_integration.simulation',
 'mission_control.estimating',
 'mission_control.execution',
 'mission_control.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyQt5>=5.15.6,<6.0.0',
 'jsonpickle>=2.2.0,<3.0.0',
 'lagom>=1.7.0,<2.0.0',
 'lxml>=4.8.0,<5.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'setuptools>=62.3.2,<63.0.0',
 'shortuuid>=1.0.9,<2.0.0']

setup_kwargs = {
    'name': 'hmrs-mission-control',
    'version': '1.0.2',
    'description': '**Heterogeneous Multi-Robots Mission Control** is an architecture for the development of applications, capable of coordinating multi-robot missions subject to uncertainty in properties of the available robots in the Software Engineering Lab (LES) at University of Brasilia.',
    'long_description': '[![Build Status](https://www.travis-ci.com/gabrielsr/hmrs_mission_control.svg?branch=master)](https://www.travis-ci.com/gabrielsr/hmrs_mission_control)\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/c40a1b3e88c74755be3423074b0b0b45)](https://www.codacy.com/gh/gabrielsr/hmrs_mission_control/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=gabrielsr/hmrs_mission_control&amp;utm_campaign=Badge_Grade)\n[![codecov](https://codecov.io/gh/gabrielsr/hmrs_mission_control/branch/master/graph/badge.svg)](https://codecov.io/gh/gabrielsr/hmrs_mission_control)\n\n\n\nHeterogeneous Multi-Robots Mission Control\n==========================================\n\n## Overview\n\n**Heterogeneous Multi-Robots Mission Control** is an architecture for the development of applications, capable of coordinating multi-robot missions subject to uncertainty in properties of the available robots in the Software Engineering Lab (LES) at University of Brasilia.\n\n**Keywords:** Software architecture, cooperative heterogeneous robots, multi-robots systems, Cyber-physical systems\n\n### License\n\nThe source code is released under a [MIT license](LICENSE).\n\n**Authors: Gabriel Rodrigues, Vicente Moraes and Gabriel F P Araujo <br />\nAffiliation: [LES](http://les.unb.br//)<br />\nMaintainers: [Gabriel Rodrigues](mailto:gabrielsr@gmail.com), [Vicente Moraes](mailto:vicenteromeiromoraes@gmail.com),[Gabriel F P Araujo](mailto:gabriel.fp.araujo@gmail.com)**\n\n**Heterogeneous Multi-Robots Mission Control** is research code, expect that it changes often and any fitness for a particular purpose is disclaimed.\n\nEnvironment dependencies\n-------------\npython 3, pip\n\nUsed IDE: vscode, plugin python\n\nmacOS aditional dependencies\nbrew install libmagic\n\nDevelopment\n---\n\nInstall poetry\n------------- \n\npoetry easy the process of managing python dependencies\n\nPIP\n```console\n$ pip install poetry\n```\n\nAlternatively, macOS brew\n```console\n$ brew install poetry \n```\n\nInstall dependencies\n--------------------\n\nInside the project folder (after clone)\n\n```console\n$ poetry install\n$ poetry shell\n```\n\nRun a Controlled Experiment\n------\nInside poetry environment (after poetry shell)\n\n```console\n python evaluation/experiment_gen_lab_samples/experiment_gen.py\n```\n\n\nTest\n----\n\nTests should be put on /tests folder and are executed with the following command.\n\n```console\n $ poetry run pytest -v --cov .\n```\n\nLinter\n------\n\n```console\n $ flake8 --statistics\n```\n\n\nRun\n---\n\nSelect the exec shell\n\n```console\n$ poetry shell\n```\n\nThen, Execute Simulation\n\n```console\n$ python ./run.py\n```\n\nDependency\n----------\n\nAdd New Dependency\n------------------\n\nTo add new dependencies use the following command.\n\n```console\n$ poetry install [name]\n```\n\nThis command will add the dependency to the Pipfile and poetry.lock assuring that the execution can be reproduced in another environment (after dependencies are updated with `poetry install` command )\n\nAdd New Dev Dependency\n----------------------\nSame as previous dependencies, but for development libraries such as the ones used for test.\n\n```console\n$ poetry install [name] --dev\n```\nNote that other systems after pulling updates will need a reexecution of `poetry install --dev`\n',
    'author': 'Gabriel Rodrigues',
    'author_email': 'gabrielsr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
