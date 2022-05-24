# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycarus',
 'pycarus.benchmarks',
 'pycarus.benchmarks.pcd',
 'pycarus.datasets',
 'pycarus.geometry',
 'pycarus.learning',
 'pycarus.learning.models',
 'pycarus.metrics',
 'pycarus.metrics.external',
 'pycarus.transforms']

package_data = \
{'': ['*'], 'pycarus': ['wheels/*']}

install_requires = \
['einops>=0.4,<0.5',
 'h5py>=3.1.0,<4.0.0',
 'ninja>=1.10.0,<2.0.0',
 'open3d>=0.15,<0.16',
 'pykdtree>=1.3.4,<2.0.0',
 'scikit-image>=0.19,<0.20',
 'torch-geometric>=2.0.2,<3.0.0',
 'types-setuptools>=57.0.0,<58.0.0']

setup_kwargs = {
    'name': 'pycarus',
    'version': '0.7.1',
    'description': 'Utilities for computer vision and 3D geometry',
    'long_description': None,
    'author': 'Luca De Luigi',
    'author_email': 'lucadeluigi91@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9.0',
}


setup(**setup_kwargs)
