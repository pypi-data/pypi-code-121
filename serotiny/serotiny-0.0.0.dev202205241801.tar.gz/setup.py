# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hydra_plugins',
 'hydra_plugins.serotiny_search_path',
 'hydra_plugins.serotiny_shell_plugin',
 'serotiny',
 'serotiny.cli',
 'serotiny.cli._utils',
 'serotiny.cli.config_cli',
 'serotiny.cli.dataframe_cli',
 'serotiny.config',
 'serotiny.config.defaults',
 'serotiny.datamodules',
 'serotiny.io',
 'serotiny.io.dataframe',
 'serotiny.io.dataframe.loaders',
 'serotiny.losses',
 'serotiny.ml_ops',
 'serotiny.models',
 'serotiny.models.utils',
 'serotiny.models.vae',
 'serotiny.models.vae.priors',
 'serotiny.networks',
 'serotiny.networks.basic_cnn',
 'serotiny.networks.layers',
 'serotiny.networks.mlp',
 'serotiny.networks.utils',
 'serotiny.networks.vae',
 'serotiny.transforms',
 'serotiny.transforms.dataframe',
 'serotiny.transforms.image']

package_data = \
{'': ['*'],
 'serotiny.config.defaults': ['data/*',
                              'mlflow/*',
                              'model/*',
                              'model/vae/*',
                              'trainer/*']}

install_requires = \
['PyYAML==6.0',
 'aicsimageio==4.6.4',
 'fire==0.4.0',
 'fsspec>=2022.3.0,<2023.0.0',
 'hydra-core>=1.2.0.dev2',
 'joblib==1.1.0',
 'makefun==1.13.1',
 'mlflow>=1.23.1',
 'nbformat==5.2.0',
 'numpy>=1.18',
 'omegaconf==2.1.1',
 'packaging==20.9',
 'pandas>=1.1',
 'pyarrow==7.0.0',
 'pycryptodome>=3.14.1,<4.0.0',
 'pytorch-lightning>=1.5.0',
 's3fs>=2022.3.0,<2023.0.0',
 'scikit-learn==1.0.2',
 'torch>=1.7.1',
 'universal-pathlib>=0.0.18,<0.0.19']

extras_require = \
{'docs': ['sphinx', 'furo', 'm2r2']}

entry_points = \
{'console_scripts': ['serotiny = serotiny.cli.cli:main',
                     'serotiny.predict = serotiny.cli.cli:main',
                     'serotiny.test = serotiny.cli.cli:main',
                     'serotiny.train = serotiny.cli.cli:main']}

setup_kwargs = {
    'name': 'serotiny',
    'version': '0.0.0.dev202205241801',
    'description': 'A framework of tools to structure, configure and drive deep learning projects',
    'long_description': "# serotiny\n\nWhile going about the work of building deep learning projects, several simultaneous problems seemed to emerge:\n\n* How do we reuse as much work from previous projects as possible, and focus on building the part of the project that makes it distinct?\n* How can we automate the generation of new models that are based on existing models, but vary in a crucial yet non-trivial way?\n* When generating a multiplicity of related models, how can we keep all of the results, predictions, and analyses straight?\n* How can the results from any number of trainings and predictions be compared and integrated in an insightful yet generally applicable way?\n\nSerotiny arose from the need to address these issues and convert the complexity of deep learning projects into something simple, reproducible, configurable, and automatable at scale.\n\nSerotiny is still a work-in-progress, but as we go along the solutions to these problems become more clear. Maybe you've run into similar situations? We'd love to hear from you.\n\n## Overview\n\n`serotiny` is a framework and set of tools to structure, configure and drive deep\nlearning projects, developed with the intention of streamlining the lifecycle of\ndeep learning projects at [Allen Institute for Cell Science](https://www.allencell.org/).\n\nIt achieves this goal by:\n\n- Standardizing the structure of DL projects\n- Relying on the modularity afforded by this standard structure to make DL projects highly\n  configurable, using [hydra](https://hydra.cc) as the framework for configuration\n- Making it easy to adopt best-practices and latest-developments in DL infrastructure\n  by tightly integrating with\n    - [Pytorch Lightning](https://pytorchlightning.ai) for neural net training/testing/prediction\n    - [MLFlow](https://mlflow.org) for experiment tracking and artifact management\n\nIn doing so, DL projects become reproducible, easy to collaborate on and can\nbenefit from general and powerful tooling.\n\n## Getting started\n\nFor more information, check our [documentation](https://allencell.github.io/serotiny),\nor jump straight into our [getting started](https://allencell.github.io/serotiny/getting_started.html)\npage, and learn how training a DL model can be as simple as:\n\n``` sh\n\n$ serotiny train data=my_dataset model=my_model\n\n```\n\n## Authors\n\n- Guilherme Pires @colobas\n- Ryan Spangler @prismofeverything\n- Ritvik Vasan @ritvikvasan\n- Caleb Chan @calebium\n- Theo Knijnenburg @tknijnen\n- Nick Gomez @gomeznick86\n\n## Citing\n\nIf you find serotiny useful, please cite this repository as:\n\n```\nSerotiny Authors (2022). Serotiny: a framework of tools to structure, configure and drive deep learning projects [Computer software]. GitHub. https://github.com/AllenCellModeling/serotiny\nFree software: BSD-3-Clause\n```\n",
    'author': 'Guilherme Pires',
    'author_email': 'guilherme.pires@alleninstitute.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://allencell.github.io/serotiny',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
