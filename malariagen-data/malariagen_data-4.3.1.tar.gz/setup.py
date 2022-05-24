# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['malariagen_data']

package_data = \
{'': ['*']}

install_requires = \
['BioPython',
 'bokeh',
 'dask[array]',
 'fsspec',
 'gcsfs',
 'igv-notebook',
 'importlib_metadata',
 'ipinfo',
 'ipyleaflet',
 'ipywidgets',
 'numba',
 'numpy',
 'pandas',
 'plotly',
 'scikit-allel',
 'scipy',
 'statsmodels',
 'tqdm',
 'xarray',
 'zarr']

setup_kwargs = {
    'name': 'malariagen-data',
    'version': '4.3.1',
    'description': 'A package for accessing and analysing MalariaGEN data.',
    'long_description': None,
    'author': 'Alistair Miles',
    'author_email': 'alistair.miles@sanger.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
