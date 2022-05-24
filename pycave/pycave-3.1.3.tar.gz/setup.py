# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycave',
 'pycave.bayes',
 'pycave.bayes.core',
 'pycave.bayes.gmm',
 'pycave.bayes.markov_chain',
 'pycave.clustering',
 'pycave.clustering.kmeans',
 'pycave.utils']

package_data = \
{'': ['*']}

install_requires = \
['lightkit>=0.4.4,<0.5.0',
 'numpy>=1.20.3,<2.0.0',
 'pytorch-lightning>=1.6.0,<2.0.0',
 'torch>=1.8.0,<2.0.0',
 'torchmetrics>=0.5.1,<0.6.0']

setup_kwargs = {
    'name': 'pycave',
    'version': '3.1.3',
    'description': 'Traditional Machine Learning Models in PyTorch.',
    'long_description': '# PyCave\n\n![PyPi](https://img.shields.io/pypi/v/pycave?label=version)\n![License](https://img.shields.io/pypi/l/pycave)\n\nPyCave allows you to run traditional machine learning models on CPU, GPU, and even on multiple\nnodes. All models are implemented in [PyTorch](https://pytorch.org/) and provide an `Estimator` API\nthat is fully compatible with [scikit-learn](https://scikit-learn.org/stable/).\n\nFor Gaussian mixture model, PyCave allows for 100x speed ups when using a GPU and enables to train\non markedly larger datasets via mini-batch training. The full suite of benchmarks run to compare\nPyCave models against scikit-learn models is available on the\n[documentation website](https://pycave.borchero.com/sites/benchmark.html).\n\n_PyCave version 3 is a complete rewrite of PyCave which is tested much more rigorously, depends on\nwell-maintained libraries and is tuned for better performance. While you are, thus, highly\nencouraged to upgrade, refer to [pycave-v2.borchero.com](https://pycave-v2.borchero.com) for\ndocumentation on PyCave 2._\n\n## Features\n\n- Support for GPU and multi-node training by implementing models in PyTorch and relying on\n  [PyTorch Lightning](https://www.pytorchlightning.ai/)\n- Mini-batch training for all models such that they can be used on huge datasets\n- Well-structured implementation of models\n\n  - High-level `Estimator` API allows for easy usage such that models feel and behave like in\n    scikit-learn\n  - Medium-level `LightingModule` implements the training algorithm\n  - Low-level PyTorch `Module` manages the model parameters\n\n## Installation\n\nPyCave is available via `pip`:\n\n```bash\npip install pycave\n```\n\nIf you are using [Poetry](https://python-poetry.org/):\n\n```bash\npoetry add pycave\n```\n\n## Usage\n\nIf you\'ve ever used scikit-learn, you\'ll feel right at home when using PyCave. First, let\'s create\nsome artificial data to work with:\n\n```python\nimport torch\n\nX = torch.cat([\n    torch.randn(10000, 8) - 5,\n    torch.randn(10000, 8),\n    torch.randn(10000, 8) + 5,\n])\n```\n\nThis dataset consists of three clusters with 8-dimensional datapoints. If you want to fit a K-Means\nmodel, to find the clusters\' centroids, it\'s as easy as:\n\n```python\nfrom pycave.clustering import KMeans\n\nestimator = KMeans(3)\nestimator.fit(X)\n\n# Once the estimator is fitted, it provides various properties. One of them is\n# the `model_` property which yields the PyTorch module with the fitted parameters.\nprint("Centroids are:")\nprint(estimator.model_.centroids)\n```\n\nDue to the high-level estimator API, the usage for all machine learning models is similar. The API\ndocumentation provides more detailed information about parameters that can be passed to estimators\nand which methods are available.\n\n### GPU and Multi-Node training\n\nFor GPU- and multi-node training, PyCave leverages PyTorch Lightning. The hardware that training\nruns on is determined by the\n[Trainer](https://pytorch-lightning.readthedocs.io/en/latest/api/pytorch_lightning.trainer.trainer.html#pytorch_lightning.trainer.trainer.Trainer)\nclass. It\'s\n[**init**](https://pytorch-lightning.readthedocs.io/en/latest/api/pytorch_lightning.trainer.trainer.html#pytorch_lightning.trainer.trainer.Trainer.__init__)\nmethod provides various configuration options.\n\nIf you want to run K-Means with a GPU, you can pass the option `gpus=1` to the estimator\'s\ninitializer:\n\n```python\nestimator = KMeans(3, trainer_params=dict(gpus=1))\n```\n\nSimilarly, if you want to train on 4 nodes simultaneously where each node has one GPU available,\nyou can specify this as follows:\n\n```python\nestimator = KMeans(3, trainer_params=dict(num_nodes=4, gpus=1))\n```\n\nIn fact, **you do not need to change anything else in your code**.\n\n### Implemented Models\n\nCurrently, PyCave implements three different models:\n\n- [GaussianMixture](https://pycave.borchero.com/sites/generated/bayes/gmm/pycave.bayes.GaussianMixture.html)\n- [MarkovChain](https://pycave.borchero.com/sites/generated/bayes/markov_chain/pycave.bayes.MarkovChain.html)\n- [K-Means](https://pycave.borchero.com/sites/generated/clustering/kmeans/pycave.clustering.KMeans.html)\n\n## License\n\nPyCave is licensed under the [MIT License](https://github.com/borchero/pycave/blob/main/LICENSE).\n',
    'author': 'Oliver Borchert',
    'author_email': 'borchero@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/borchero/pycave',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
