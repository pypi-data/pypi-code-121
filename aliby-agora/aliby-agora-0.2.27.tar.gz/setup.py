# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['agora', 'agora.io', 'agora.utils', 'logfile_parser']

package_data = \
{'': ['*'], 'logfile_parser': ['grammars/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'h5py==2.10',
 'numpy>=1.6.0',
 'opencv-python',
 'pandas>=1.1.4,<2.0.0',
 'py-find-1st>=1.1.5,<2.0.0',
 'scipy>=1.7.3']

setup_kwargs = {
    'name': 'aliby-agora',
    'version': '0.2.27',
    'description': 'A gathering of shared utilities for the Swain Lab image processing pipeline.',
    'long_description': '# Agora\nShared tools for data processing within the aliby pipeline.\n\n## Installation\n\nIf you just want to use the tools.\n\n```bash\n> pip install aliby-argo\n```\n\nOr, for development, clone this repository and then install using pip:\n\n```bash\n> pip install -e argo/\n```\n\n\n',
    'author': 'Alán Muñoz',
    'author_email': 'amuoz@ed.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
