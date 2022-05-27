# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['embeddings',
 'embeddings.config',
 'embeddings.data',
 'embeddings.embedding',
 'embeddings.embedding.static',
 'embeddings.evaluator',
 'embeddings.metric',
 'embeddings.model',
 'embeddings.model.lightning_module',
 'embeddings.pipeline',
 'embeddings.task',
 'embeddings.task.flair_task',
 'embeddings.task.lightning_task',
 'embeddings.task.sklearn_task',
 'embeddings.transformation',
 'embeddings.transformation.flair_transformation',
 'embeddings.transformation.hf_transformation',
 'embeddings.transformation.pandas_transformation',
 'embeddings.utils',
 'embeddings.utils.lightning_callbacks',
 'experimental',
 'experimental.datasets',
 'experimental.datasets.utils',
 'experimental.embeddings',
 'experimental.embeddings.language_models',
 'experimental.embeddings.scripts',
 'experimental.embeddings.static']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.2.0',
 'appdirs>=1.4.4',
 'click==8.0.4',
 'datasets>=1.16.1',
 'flair>=0.9',
 'numpy>=1.20.0',
 'optuna>=2.9.1',
 'pydantic>=1.8.2',
 'pytorch-lightning==1.5.4',
 'requests>=2.25.1',
 'scikit-learn>=1.0.0',
 'seqeval>=1.2.2',
 'srsly>=2.4.1',
 'tensorboard>=2.4.1',
 'torch>=1.9',
 'transformers>=4.12.5',
 'typer>=0.4.0',
 'types-PyYAML>=5.4.10',
 'types-setuptools>=57.4.11',
 'wandb>=0.12.10']

extras_require = \
{':extra == "developer"': ['typing-extensions>=4.0.1'],
 ':sys_platform == "win32"': ['intel-openmp>=2022.0.3,<2023.0.0'],
 'pymagnitude': ['annoy>=1.17.0', 'lz4>=3.1.10', 'pymagnitude>=0.1.143']}

setup_kwargs = {
    'name': 'clarinpl-embeddings',
    'version': '0.0.1rc239915525894',
    'description': '',
    'long_description': None,
    'author': 'Roman Bartusiak',
    'author_email': 'riomus@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CLARIN-PL/embeddings',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8.0,<4.0',
}


setup(**setup_kwargs)
