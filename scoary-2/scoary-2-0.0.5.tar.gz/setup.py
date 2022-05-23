# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scoary']

package_data = \
{'': ['*'], 'scoary': ['templates/*']}

install_requires = \
['fast-fisher>=0.0.4,<0.0.5',
 'fire>=0.4.0,<0.5.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numba>=0.55.1,<0.56.0',
 'pandas>=1.4.0,<2.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'statsmodels>=0.13.2,<0.14.0']

entry_points = \
{'console_scripts': ['scoary = scoary.scoary:main']}

setup_kwargs = {
    'name': 'scoary-2',
    'version': '0.0.5',
    'description': 'Scoary 2: Associate genes with traits!',
    'long_description': None,
    'author': 'MrTomRod',
    'author_email': 'roder.thomas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
