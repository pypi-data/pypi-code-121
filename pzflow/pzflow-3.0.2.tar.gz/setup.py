# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pzflow']

package_data = \
{'': ['*'], 'pzflow': ['example_files/*']}

install_requires = \
['dill>=0.3.4,<0.4.0',
 'jax>=0.3.5,<0.4.0',
 'jaxlib>=0.3.5,<0.4.0',
 'optax>=0.1.2,<0.2.0',
 'pandas>=1.1',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'pzflow',
    'version': '3.0.2',
    'description': 'Probabilistic modeling of tabular data with normalizing flows.',
    'long_description': '![build](https://github.com/jfcrenshaw/pzflow/workflows/build/badge.svg)\n[![codecov](https://codecov.io/gh/jfcrenshaw/pzflow/branch/main/graph/badge.svg?token=qR5cey0swQ)](https://codecov.io/gh/jfcrenshaw/pzflow)\n[![PyPI version](https://badge.fury.io/py/pzflow.svg)](https://badge.fury.io/py/pzflow)\n[![DOI](https://zenodo.org/badge/327498448.svg)](https://zenodo.org/badge/latestdoi/327498448)\n[![Docs](https://img.shields.io/badge/Docs-https%3A%2F%2Fjfcrenshaw.github.io%2Fpzflow%2F-red)](https://jfcrenshaw.github.io/pzflow/)\n\n# PZFlow\n\nPZFlow is a python package for probabilistic modeling of tabular data with normalizing flows.\n\nIf your data consists of continuous variables that can be put into a Pandas DataFrame, pzflow can model the joint probability distribution of your data set.\n\nThe `Flow` class makes building and training a normalizing flow simple.\nIt also allows you to easily sample from the normalizing flow (e.g., for forward modeling or data augmentation), and calculate posteriors over any of your variables.\n\nThere are several tutorial notebooks in the [docs](https://jfcrenshaw.github.io/pzflow/tutorials/).\n\n## Installation\n\nSee the instructions in the [docs](https://jfcrenshaw.github.io/pzflow/install/).\n\n## Citation\n\nWe are preparing a paper on pzflow.\nIf you use this package in your research, please check back here for a citation before publication.\nIn the meantime, please cite the [Zenodo release](https://zenodo.org/badge/latestdoi/327498448).\n\n### Sources\n\nPZFlow was originally designed for forward modeling of photometric redshifts as a part of the Creation Module of the [DESC](https://lsstdesc.org/) [RAIL](https://github.com/LSSTDESC/RAIL) project.\nThe idea to use normalizing flows for photometric redshifts originated with [Bryce Kalmbach](https://github.com/jbkalmbach).\nThe earliest version of the normalizing flow in RAIL was based on a notebook by [Francois Lanusse](https://github.com/eiffl) and included contributions from [Alex Malz](https://github.com/aimalz).\n\nThe functional jax structure of the bijectors was originally based on [`jax-flows`](https://github.com/ChrisWaites/jax-flows) by [Chris Waites](https://github.com/ChrisWaites). The implementation of the Neural Spline Coupling is largely based on the [Tensorflow implementation](https://github.com/tensorflow/probability/blob/master/tensorflow_probability/python/bijectors/rational_quadratic_spline.py), with some inspiration from [`nflows`](https://github.com/bayesiains/nflows/).\n\nNeural Spline Flows are based on the following papers:\n\n  > [NICE: Non-linear Independent Components Estimation](https://arxiv.org/abs/1410.8516)\\\n  > Laurent Dinh, David Krueger, Yoshua Bengio\\\n  > _arXiv:1410.8516_\n\n  > [Density estimation using Real NVP](https://arxiv.org/abs/1605.08803)\\\n  > Laurent Dinh, Jascha Sohl-Dickstein, Samy Bengio\\\n  > _arXiv:1605.08803_\n\n  > [Neural Spline Flows](https://arxiv.org/abs/1906.04032)\\\n  > Conor Durkan, Artur Bekasov, Iain Murray, George Papamakarios\\\n  > _arXiv:1906.04032_\n',
    'author': 'John Franklin Crenshaw',
    'author_email': 'jfcrenshaw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jfcrenshaw/pzflow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
