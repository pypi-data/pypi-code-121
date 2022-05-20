# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['volcano_cooking',
 'volcano_cooking.configurations',
 'volcano_cooking.helper_scripts',
 'volcano_cooking.modules.convert',
 'volcano_cooking.modules.create',
 'volcano_cooking.plotting']

package_data = \
{'': ['*']}

install_requires = \
['PyWavelets>=1.1.1,<2.0.0',
 'cftime>=1.5.0,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'cosmoplots>=0.1.5,<0.2.0',
 'dask>=2022.3.0,<2023.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'netCDF4>=1.5.8,<2.0.0',
 'numpy>=1.21.1,<2.0.0',
 'scipy>=1.7.1,<2.0.0',
 'superposed-pulses>=1.2,<2.0',
 'wget>=3.2,<4.0',
 'xarray>=0.21.1,<0.22.0']

entry_points = \
{'console_scripts': ['sfrc-sparse2lin = volcano_cooking.sparse_to_lin:main',
                     'view-frc = volcano_cooking.view_force:main',
                     'volcano-cooking = volcano_cooking.__main__:main']}

setup_kwargs = {
    'name': 'volcano-cooking',
    'version': '0.7.0',
    'description': 'Make some volcanoes and simulate them in CESM2',
    'long_description': None,
    'author': 'engeir',
    'author_email': 'eirroleng@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
