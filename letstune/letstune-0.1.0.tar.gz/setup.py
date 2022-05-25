# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['letstune',
 'letstune.backend',
 'letstune.backend.repo',
 'letstune.backend.runner',
 'letstune.backend.scheduler',
 'letstune.results']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.3,<2.0.0', 'pandas>=1.4.2,<2.0.0']

setup_kwargs = {
    'name': 'letstune',
    'version': '0.1.0',
    'description': 'Hyper-parameter tuning for the masses!',
    'long_description': '<div align="center">\n  <img src="img/logo.svg"><br>\n</div>\n\n-----------------\n\n# letstune\n\n*Hyper-parameter tuning for the masses!*\n\n![License: MIT](https://img.shields.io/badge/license-MIT-purple.svg)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat)](https://pycqa.github.io/isort/)\n\n## Why?\n\n### Do you know good *number of layers* or *learning rate*?\n\n**No?** I also don\'t. :wink:\n\n_letstune_ tries various parameter configurations and gives you back\nthe best model.\n\n### Do you have *excess* of time or cloud resources?\n\n**Nobody has!** :alarm_clock:\n\nWhen training neural network or doing gradient boosting,\n_letstune_ spends most of the time on the most promising\nparameters.\n\n_letstune_ makes a kind of :moneybag: investment rounds.\n\nAt the first round, it evaluates all parameters for a few epochs.\n\nOnly 25% of trainings will advance to the next round.\nTrainings with the lowest metric value are automatically dropped.\n\n### Are you a *hard worker*?\n\n**Neither do I.** :sunglasses:\n\nCommon tasks in _letstune_ are realized with Python one-liners:\n\n* get the best model: `model = tuning[0].best_epoch.checkpoint.load_pickle()`\n* get Pandas summary dataframe with *parameters* and *metric values*: `df = tuning.to_df()`\n\n### Additionally:\n\nWorks with your favourite ML library :snake: - it\'s *library agnostic*!\n\n*Resumes work* from the point, where program was stopped.\n\nPermissive *business-friendly* MIT license.\n\n## Great! How to use it?\n\nFirst, define your *parameters*:\n\n```python\nimport letstune\nfrom letstune import rand\n\nclass SGDClassifierParams(letstune.ModelParams[SGDClassifier]):\n    average: bool\n    l1_ratio: float = rand.uniform(0, 1)\n    alpha: float = rand.uniform(1e-2, 1e0, log=True)\n```\n\nThen define a *trainer*.\n*Trainer* is an object, which knows how to *train* a model!\n\n```python\nclass DigitsTrainer(letstune.SimpleTrainer[SGDClassifierParams]):\n    metric = letstune.Metric("accuracy")\n\n    def load_dataset(self, dataset):\n        self.X_train, self.X_test, self.y_train, self.y_test = dataset\n\n    def train(self, params):\n        # params has type SGDClassifierParams\n\n        # letstune provides method create_model\n        # returning SGDClassifier\n        model = params.create_model(\n            loss="hinge",\n            penalty="elasticnet",\n            fit_intercept=True,\n            random_state=42,\n        )\n        model.fit(self.X_train, self.y_train)\n\n        accuracy = model.score(self.X_test, self.y_test)\n\n        return model, {"accuracy": accuracy}\n\n\ntrainer = DigitsTrainer()  # new instance!\n```\n\nNeural networks and gradient boosting trainings\ncan be based on `letstune.EpochTrainer`,\nwhich has `train_epoch` method.\n\nFinally, *let\'s tune*!\n\n```python\ntuning = letstune.tune(\n    trainer,\n    16,  # number of tested random parameters\n    dataset=(X_train, X_test, y_train, y_test),\n    results_dir="digits_tuning",\n)\n```\n\n*Our model* is ready to use:\n\n```python\nmodel = tuning[0].checkpoint.load_pickle()\n```\n\nDon\'t forget to check out [examples directory](examples)! :eyes:\n\n## References\n\n*A System for Massively Parallel Hyperparameter Tuning* by Li et al.;\n[arXiv:1810.05934](https://arxiv.org/abs/1810.05934)\n\nOverview of various hyperparameter-tuning algorithms.\n_letstune_ implements a variant of Successive Halving.\n',
    'author': 'Michał Słapek',
    'author_email': '28485371+mslapek@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
