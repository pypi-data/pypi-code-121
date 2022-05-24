# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['black_it',
 'black_it.loss_functions',
 'black_it.plot',
 'black_it.samplers',
 'black_it.utils']

package_data = \
{'': ['*']}

install_requires = \
['GPy>=1.10.0,<2.0.0',
 'ipywidgets>=7.7.0,<8.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.22.3,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'scikit-learn>=1.1.0,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'statsmodels>=0.13.2,<0.14.0']

setup_kwargs = {
    'name': 'black-it',
    'version': '0.1.0.dev1',
    'description': 'black-it: Black-box abm calibration kit',
    'long_description': '\n<p align="center">\n<img src="docs/logo/logo_1024.png" width="500">\n<sup><a href="#footnote-1">*</a></sup>\n</p>\n\n<a href="https://github.com/bancaditalia/black-it/blob/main/LICENSE">\n    <img alt="GitHub" src="https://img.shields.io/github/license/bancaditalia/black-it">\n</a>\n\n\n# Black-box abm calibration kit\n\nBlack-it is an easy-to-use toolbox designed to help you calibrate the parameters\nin your agent-based models and simulations (ABMs), using state-of-the-art\ntechniques to sample the parameter search space, with no need to reinvent the\nwheel.\n\nModels from economics, epidemiology, biology, logistics, and more can be dealt\nwith. The software can be used as-is - if your main interest is the ABM model\nitself. However, in case your research thing is to, e.g., devise new sampling\nstrategies for ginormous search spaces and highly non-linear model, then you can\ndeploy and test your new ideas on a solid, reusable, modular foundation, in a\nmatter of days, with no need to reimplement all the plumbings from scratch.\n\n## Installation\n\nThis project requires Python v3.8 or later.\n\nTo install the latest version of the package from [PyPI](https://pypi.org/project/black-it/):\n```\npip install black-it\n```\n\nOr, directly from GitHub:\n\n```\npip install git+https://github.com/bancaditalia/black-it.git#egg=black-it\n```\n\nIf you\'d like to contribute to the package, please read the [CONTRIBUTING.md](./CONTRIBUTING.md) guide.\n\n## Quick Example\n\nThe GitHub repo of Black-it contains a series ready-to-run calibration examples.\n\nTo experiment with them, simply clone the repo and enter the `examples` folder\n\n```\ngit clone https://github.com/bancaditalia/black-it.git\ncd black-it/examples\n```\n\nYou\'ll find several scripts and notebooks. The following is the script named `main.py`\n\n```python\nimport models.simple_models as md\nimport numpy as np\n\nfrom black_it.calibrator import Calibrator\nfrom black_it.loss_functions.msm import MethodOfMomentsLoss\nfrom black_it.samplers.best_batch import BestBatchSampler\nfrom black_it.samplers.halton import HaltonSampler\nfrom black_it.samplers.random_forest import RandomForestSampler\n\ntrue_params = [0.20, 0.20, 0.75]\nbounds = [\n    [0.10, 0.10, 0.10],  # LOWER bounds\n    [1.00, 1.00, 1.00],  # UPPER bounds\n]\nbounds_step = [0.01, 0.01, 0.01]  # Step size in range between bounds\n\nbatch_size = 8\nhalton_sampler = HaltonSampler(batch_size=batch_size)\nrandom_forest_sampler = RandomForestSampler(batch_size=batch_size)\nbest_batch_sampler = BestBatchSampler(batch_size=batch_size)\n\n# define a model to be calibrated\nmodel = md.MarkovC_KP\n\n# generate a synthetic dataset to test the calibrator\nN = 1500\nseed = 1\nreal_data = model(true_params, N, seed)\n\n# define a loss\nloss = MethodOfMomentsLoss()\n\n# initialize a Calibrator object\ncal = Calibrator(\n    samplers=[halton_sampler, random_forest_sampler, best_batch_sampler],\n    real_data=real_data,\n    model=model,\n    parameters_bounds=np.asarray(bounds),\n    parameters_precision=np.asarray(bounds_step),\n    ensemble_size=1,\n    loss_function=loss,\n)\n\n# calibrate the model\nparams, losses = cal.calibrate(n_batches=4)\n\nprint(f"True parameters:       {true_params}")\nprint(f"Best parameters found: {params[0]}")\n```\n\nWhen the calibration terminates (~half a minute), towards the end  of the output\nyou should see the following messages:\n```\nTrue parameters:       [0.2, 0.2, 0.75]\nBest parameters found: [0.21 0.2  0.76]\n```\n\n## Docs\n\nTo view the documentation click [here](https://bancaditalia.github.io/black-it/).\n\n## Disclaimer\n\nThis package is an outcome of a research project. All errors are those of the authors. All views expressed are personal views, not those of Bank of Italy.\n\n---\n\n<p id="footnote-1">\n* Credits to <a href="https://www.bankit.art/people/sara-corbo">Sara Corbo</a> for the logo.\n</p>\n',
    'author': 'Applied Research Team',
    'author_email': 'appliedresearchteam@bancaditalia.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bancaditalia/black-it',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
