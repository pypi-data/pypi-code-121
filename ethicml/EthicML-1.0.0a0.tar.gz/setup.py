# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ethicml',
 'ethicml.algorithms',
 'ethicml.algorithms.inprocess',
 'ethicml.algorithms.postprocess',
 'ethicml.algorithms.preprocess',
 'ethicml.data',
 'ethicml.data.csvs',
 'ethicml.data.tabular_data',
 'ethicml.evaluators',
 'ethicml.implementations',
 'ethicml.implementations.adv_debiasing_modules',
 'ethicml.implementations.dro_modules',
 'ethicml.implementations.fair_dummies_modules',
 'ethicml.implementations.hgr_modules',
 'ethicml.implementations.hgr_modules.facl',
 'ethicml.implementations.vfae_modules',
 'ethicml.metrics',
 'ethicml.preprocessing',
 'ethicml.utility',
 'ethicml.visualisation']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.20,<4.0.0',
 'Pillow>=9.0.1,<10.0.0',
 'folktables>=0.0.11,<0.0.12',
 'gitdb2==4.0.2',
 'joblib>=1.1.0,<2.0.0',
 'matplotlib>=3.0.2',
 'numpy>=1.20.1',
 'pandas>=1.0,<2.0',
 'pipenv>=2018.11.26',
 'ranzen>=1.1.1,<2.0.0',
 'scikit-learn>=0.20.1',
 'scipy>=1.7.2,<2.0.0',
 'seaborn>=0.9.0',
 'smmap2==3.0.1',
 'teext>=0.1.3,<0.2.0',
 'tqdm>=4.31.1',
 'typing-extensions>=4.0']

extras_require = \
{'all': ['fairlearn==0.7.0', 'cloudpickle>=2.0.0,<3.0.0'],
 'ci': ['fairlearn==0.7.0',
        'cloudpickle>=2.0.0,<3.0.0',
        'pytest>=6.2.2,<8.0.0',
        'pytest-cov>=2.6,<4.0',
        'omegaconf>=2.2.1']}

setup_kwargs = {
    'name': 'ethicml',
    'version': '1.0.0a0',
    'description': "EthicML is a library for performing and assessing algorithmic fairness. Unlike other libraries, EthicML isn't an education tool, but rather a researcher's toolkit.",
    'long_description': '# EthicML: A featureful framework for developing fair algorithms\n\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n![](https://github.com/predictive-analytics-lab/EthicML/workflows/EthicML%20CI/badge.svg)\n\n\n\nEthicML is a library for performing and assessing __algorithmic fairness__.\nUnlike other libraries, EthicML isn\'t an education tool, but rather a __researcher__\'s toolkit.\n\nOther algorthimic fairness packages are useful, but given that we primarily do research,\na lot of the work we do doesn\'t fit into some nice box.\nFor example, we might want to use a \'fair\' pre-processing method on the data before training a classifier on it.\nWe may still be experimenting and only want part of the framework to execute,\nor we may want to do hyper-parameter optimization.\nWhilst other frameworks can be modified to do these tasks,\nyou end up with hacked-together approaches that don\'t lend themselves to be built on in the future.\nBecause of this, we built EthicML, a fairness toolkit for researchers.\n\nFeatures include:\n- Support for multiple sensitive attributes\n- Vision datasets\n- Codebase typed with mypy\n- Tested code\n- Reproducible results\n\n### Why not use XXX?\n\nThere are an increasing number of other options,\nIBM\'s fair-360, Aequitas, EthicalML/XAI, Fairness-Comparison and others.\nThey\'re all great at what they do, they\'re just not right for us.\nWe will however be influenced by them.\nWhere appropriate, we even subsume some of these libraries.\n\n## Installation\n\nEthicML requires Python >= 3.7.\nTo install EthicML, just do\n```\npip3 install ethicml\n```\n\nIf you want to use the method by Agarwal et al., you have to explicitly install _all_ dependencies:\n```\npip3 install \'ethicml[all]\'\n```\n(The quotes are needed in `zsh` and will also work in `bash`.)\n\n**Attention**: In order to use all features of EthicML, PyTorch needs to be installed separately.\nWe are not including PyTorch as a requirement of EthicML,\nbecause there are many different versions for different systems.\n\n## Documentation\n\nThe documentation can be found here: https://wearepal.ai/EthicML/\n\n## Design Principles\n\n```mermaid\nflowchart LR\n    A(Datasets) -- load --> B(Data tuples);\n    B --> C[evaluate_models];\n    G(Algorithms) --> C;\n    C --> D(Metrics);\n```\n\nKeep things simple.\n\n### The Triplet\n\nGiven that we\'re considering fairness, the base of the toolbox is the triplet {x, s, y}\n\n- X - Features\n- S - Sensitive Label\n- Y - Class Label\n\n__Developer note__: All methods must assume S and Y are multi-class.\n\nWe use a DataTuple class to contain the triplet\n\n```python\ntriplet = DataTuple(x: pandas.DataFrame, s: pandas.DataFrame, y: pandas.DataFrame)\n```\n\nIn addition, we have a variation: the TestTuple which contains the pair\n```python\npair = TestTuple(x: pandas.DataFrame, s: pandas.DataFrame)\n```\nThis is to reduce the risk of a user accidentally evaluating performance on their training set.\n\nUsing dataframes may be a little inefficient,\nbut given the amount of splicing on conditions that we\'re doing, it feels worth it.\n\n### Separation of Methods\n\nWe purposefully keep pre, during and post algorithm methods separate. This is because they have different return types.\n\n```python\npre_algorithm.run(train: DataTuple, test: TestTuple)  # -> Tuple[DataTuple, TestTuple]\nin_algorithm.run(train: DataTuple, test: TestTuple)  # -> Prediction\npost_algorithm.run(train_prediction: Prediction, train: DataTuple, test_prediction: Prediction, test: TestTuple)  # -> Prediction\n```\nwhere `Prediction` holds a pandas.Series of the class label.\nIn the case of a "soft" output, `SoftPrediction` extends `Prediction` and provides a mapping from\n"soft" to "hard" labels.\nSee the documentation for more details.\n\n### General Rules of Thumb\n\n- Mutable data structures are bad.\n- At the very least, functions should be Typed.\n- Readability > Efficiency.\n- Warnings must be addressed.\n- Always write tests first.\n\n## Future Plans\n\nThe aim is to make EthicML operate on 2 levels.\n\n1. We want a high-level API so that a user can define a new model or metric, then get publication-ready\nresults in just a couple of lines of code.\n2. We understand that truly ground-breaking work sometimes involves tearing up the rulebook.\nTherefore, we want to also expose a lower-level API so that a user can make use of as much, or little of the library\nas is suitable for them.\n\nWe\'ve built everything with this philosophy in mind, but acknowledge that we still have a way to go.\n\n# Contributing\n\nIf you\'re interest in this research area, we\'d love to have you aboard.\nFor more details check out [CONTRIBUTING.md](./CONTRIBUTING.md).\nWhether your skills are in coding-up papers you\'ve read, writing tutorials, or designing a logo, please reach out.\n\n## Development\nInstall development dependencies with `pip install -e .[dev]`\n\nTo use the pre-commit hooks run `pre-commit install`\n',
    'author': 'PAL',
    'author_email': 'info@wearepal.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/predictive-analytics-lab/EthicML',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
