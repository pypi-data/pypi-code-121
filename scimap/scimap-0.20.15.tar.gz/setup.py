# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scimap',
 'scimap.cli',
 'scimap.helpers',
 'scimap.plotting',
 'scimap.preprocessing',
 'scimap.tests',
 'scimap.tools']

package_data = \
{'': ['*'],
 'scimap.tests': ['_data/example_data.csv',
                  '_data/example_data.csv',
                  '_data/example_data.csv',
                  '_data/example_data.h5ad',
                  '_data/example_data.h5ad',
                  '_data/example_data.h5ad',
                  '_data/phenotype_workflow.csv',
                  '_data/phenotype_workflow.csv',
                  '_data/phenotype_workflow.csv']}

install_requires = \
['PhenoGraph>=1.5.7,<2.0.0',
 'TiffFile>=2020.11.18,<2021.0.0',
 'anndata>=0.7.4,<0.8.0',
 'dask[array]>=2.30.0,<3.0.0',
 'gensim>=4.0,<5.0',
 'llvmlite>=0.38.0,<0.39.0',
 'matplotlib>=3.2.1,<4.0.0',
 'mkdocs-material>=7.1.1,<8.0.0',
 'mkdocs>=1.1.2,<2.0.0',
 'napari-ome-zarr>=0.4.0,<0.5.0',
 'napari>=0.4.2,<0.5.0',
 'numba>=0.55.0',
 'numpy>=1.20.0,<2.0.0',
 'pandas>=1.0.4,<2.0.0',
 'plotly>=4.12.0,<5.0.0',
 'pytest-xvfb>=2.0.0,<3.0.0',
 'pytest>=5.4.3,<6.0.0',
 'scanpy>=1.6.0,<2.0.0',
 'scipy>=1.4.1,<2.0.0',
 'seaborn>=0.11.0,<0.12.0',
 'shapely>=1.7.1,<2.0.0',
 'sklearn>=0.0,<0.1',
 'tifffile>=2020.6.3,<2021.0.0',
 'zarr==2.10.3']

entry_points = \
{'console_scripts': ['scimap-clustering = '
                     'scimap.cli._scimap_mcmicro:clustering',
                     'scimap-mcmicro = scimap.cli._scimap_mcmicro:mcmicro_wrap',
                     'scimap-merge-h5ad = scimap.cli._scimap_mcmicro:merge']}

setup_kwargs = {
    'name': 'scimap',
    'version': '0.20.15',
    'description': 'Spatial Single-Cell Analysis Toolkit',
    'long_description': '# Single-Cell Image Analysis Package\n<br>\n\n[![build: Unix-Mac-Win](https://github.com/ajitjohnson/scimap/actions/workflows/build-unix-mac-win.yml/badge.svg)](https://github.com/ajitjohnson/scimap/actions/workflows/build-unix-mac-win.yml)\n[![Docs](https://github.com/ajitjohnson/scimap/actions/workflows/docs.yml/badge.svg)](https://github.com/ajitjohnson/scimap/actions/workflows/docs.yml)\n[![Downloads](https://pepy.tech/badge/scimap)](https://pepy.tech/project/scimap)\n[![PyPI Version](https://img.shields.io/pypi/v/scimap.svg)](https://pypi.org/project/scimap)\n[![PyPI License](https://img.shields.io/pypi/l/scimap.svg)](https://pypi.org/project/scimap)\n[![Gitter chat](https://badges.gitter.im/scimap_io/community.png)](https://gitter.im/scimap_io/community)\n[![DOI](https://zenodo.org/badge/271099296.svg)](https://zenodo.org/badge/latestdoi/271099296)\n\n<br>\n\n<img src="./docs/assets/scimap_logo.jpg" style="max-width:700px;width:100%" >\n\n<br> \n\nScimap is a scalable toolkit for analyzing spatial molecular data. The underlying framework is generalizable to spatial datasets mapped to XY coordinates. The package uses the [anndata](https://anndata.readthedocs.io/en/stable/anndata.AnnData.html) framework making it easy to integrate with other popular single-cell analysis toolkits. It includes preprocessing, phenotyping, visualization, clustering, spatial analysis and differential spatial testing. The Python-based implementation efficiently deals with large datasets of millions of cells.\n\n## Installation\n\nWe strongly recommend installing `scimap` in a fresh virtual environment.\n\n```\n# If you have conda installed\nconda create --name scimap python=3.8\nconda activate scimap\n```\n\nInstall `scimap` directly into an activated virtual environment:\n\n```python\n$ pip install scimap\n```\n\nAfter installation, the package can be imported as:\n\n```python\n$ python\n>>> import scimap as sm\n```\n\n### Notice for Apple M1 users\nPlease note that multiple python packages have not yet extended support for M1 users. \nBelow is a temporary solution to install scimap in `Apple M1` machines. \nPlease follow the instructions in the given order.\n\n```\n# create and load a new environment\nconda create -y -n scimap -c andfoy python=3.9 pyqt\nconda activate scimap\n\n# if you do not have xcode please install it\nxcode-select --install\n\n# if you do not have homebrew please install it\n/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"\n\n# if you do not have cmake install it\nbrew install cmake\n\n# install h5py\nbrew install hdf5@1.12\nHDF5_DIR=/opt/homebrew/Cellar/hdf5/ pip install --no-build-isolation h5py\n\n# install llvmlite\nconda install llvmlite -y\n\n# install leidenalg\npip install git+https://github.com/vtraag/leidenalg.git\n\n# install scimap\npip install -U scimap\n\n# uninstall \nconda remove llvmlite -y\npip uninstall numba -y\npip uninstall numpy -y\n\n# reinstall this specific version of llvmlite (ignore errors/warning)\npip install -i https://pypi.anaconda.org/numba/label/wheels_experimental_m1/simple llvmlite\n\n# reinstall this specific version of numpy (ignore errors/warning)\npip install numpy==1.22.3\n\n# reinstall this specific version of numba (ignore errors/warning)\npip install -i https://pypi.anaconda.org/numba/label/wheels_experimental_m1/simple numba\n\n```\n\n## Get Started\n\n\n#### Detailed documentation of `scimap` functions and tutorials are available [here](http://scimap.xyz/).\n\n*SCIMAP* development is led by [Ajit Johnson Nirmal](https://ajitjohnson.com/) at the Laboratory of Systems Pharmacology, Harvard Medical School.\n\n## Funding\nThis work is supported by the following NIH grant K99-CA256497\n\n',
    'author': 'Ajit Johnson Nirmal',
    'author_email': 'ajitjohnson.n@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/scimap/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
