# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reil',
 'reil.agents',
 'reil.datatypes',
 'reil.datatypes.buffers',
 'reil.environments',
 'reil.healthcare',
 'reil.healthcare.agents',
 'reil.healthcare.dosing_protocols',
 'reil.healthcare.dosing_protocols.warfarin',
 'reil.healthcare.mathematical_models',
 'reil.healthcare.subjects',
 'reil.learners',
 'reil.legacy',
 'reil.subjects',
 'reil.utils']

package_data = \
{'': ['*']}

install_requires = \
['Keras-Applications>=1.0.8,<2.0.0',
 'Keras-Preprocessing>=1.1.2,<2.0.0',
 'Markdown>=3.3.6,<4.0.0',
 'Pillow>=9.0.0,<10.0.0',
 'Werkzeug>=2.0.2,<3.0.0',
 'absl-py==0.15.0',
 'astor>=0.8.1,<0.9.0',
 'astroid==2.7.2',
 'colorama>=0.4.4,<0.5.0',
 'cycler>=0.11.0,<0.12.0',
 'dill>=0.3.4,<0.4.0',
 'gast==0.3.3',
 'google-pasta>=0.2.0,<0.3.0',
 'grpcio==1.32',
 'h5py==2.10',
 'importlib-metadata>=4.10.1,<5.0.0',
 'isort>=5.10.1,<6.0.0',
 'kiwisolver>=1.3.2,<2.0.0',
 'lazy-object-proxy>=1.7.1,<2.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'mccabe>=0.6.1,<0.7.0',
 'numpy==1.19.2',
 'openpyxl>=3.0.9,<4.0.0',
 'opt-einsum>=3.3.0,<4.0.0',
 'pandas==1.2',
 'protobuf>=3.19.3,<4.0.0',
 'pyparsing>=3.0.6,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'pytz>=2021.3,<2022.0',
 'ruamel.yaml>=0.17.20,<0.18.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'six==1.15',
 'tensorboard>=2.7.0,<3.0.0',
 'tensorflow-estimator==2.4',
 'tensorflow-probability==0.12.2',
 'tensorflow==2.4.1',
 'termcolor>=1.1.0,<2.0.0',
 'versioneer>=0.21,<0.22',
 'wrapt==1.12.1',
 'zipp>=3.7.0,<4.0.0']

setup_kwargs = {
    'name': 'reil',
    'version': '0.1.9',
    'description': '',
    'long_description': None,
    'author': 'sanzabizadeh',
    'author_email': 'sadjad-anzabizadeh@uiowa.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
