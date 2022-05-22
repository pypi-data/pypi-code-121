# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sklearn_nature_inspired_algorithms',
 'sklearn_nature_inspired_algorithms.helpers',
 'sklearn_nature_inspired_algorithms.model_selection']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5,<4.0.0',
 'niapy==2.0.1',
 'numpy>=1.22,<2.0.0',
 'pandas>=1.4,<2.0.0',
 'scikit-learn>=1.0.2',
 'scipy>=1.7.3',
 'seaborn>=0.11,<1.0.0',
 'toml>=0.10,<1.0.0']

setup_kwargs = {
    'name': 'sklearn-nature-inspired-algorithms',
    'version': '0.8.2',
    'description': 'Search using nature inspired algorithms over specified parameter values for an sklearn estimator.',
    'long_description': '# Nature-Inspired Algorithms for scikit-learn\n\n[![CI](https://github.com/timzatko/Sklearn-Nature-Inspired-Algorithms/workflows/CI/badge.svg?branch=master)](https://github.com/timzatko/Sklearn-Nature-Inspired-Algorithms/actions?query=workflow:CI+branch:master)\n[![Maintainability](https://api.codeclimate.com/v1/badges/ed99e5c765bf5c95d716/maintainability)](https://codeclimate.com/github/timzatko/Sklearn-Nature-Inspired-Algorithms/maintainability)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sklearn-nature-inspired-algorithms)\n[![PyPI version](https://badge.fury.io/py/sklearn-nature-inspired-algorithms.svg)](https://pypi.org/project/sklearn-nature-inspired-algorithms/)\n[![PyPI downloads](https://img.shields.io/pypi/dm/sklearn-nature-inspired-algorithms)](https://pypi.org/project/sklearn-nature-inspired-algorithms/)\n[![Fedora package](https://img.shields.io/fedora/v/python3-sklearn-nature-inspired-algorithms?color=blue&label=Fedora%20Linux&logo=fedora)](https://src.fedoraproject.org/rpms/python-sklearn-nature-inspired-algorithms)\n\nNature-inspired algorithms for hyper-parameter tuning of [scikit-learn](https://github.com/scikit-learn/scikit-learn) models. This package uses algorithms implementation from [NiaPy](https://github.com/NiaOrg/NiaPy). \n\n## Installation\n\n```shell script\n$ pip install sklearn-nature-inspired-algorithms\n```\n\nTo install this package on Fedora, run:\n\n```sh\n$ dnf install python3-sklearn-nature-inspired-algorithms\n```\n\n## Usage\n\nThe usage is similar to using sklearn\'s `GridSearchCV`. Refer to the [documentation](https://sklearn-nature-inspired-algorithms.readthedocs.io/en/stable/) for more detailed guides and more examples.\n\n```python\nfrom sklearn_nature_inspired_algorithms.model_selection import NatureInspiredSearchCV\nfrom sklearn.ensemble import RandomForestClassifier\n\nparam_grid = { \n    \'n_estimators\': range(20, 100, 20), \n    \'max_depth\': range(2, 40, 2),\n    \'min_samples_split\': range(2, 20, 2), \n    \'max_features\': ["auto", "sqrt", "log2"],\n}\n\nclf = RandomForestClassifier(random_state=42)\n\nnia_search = NatureInspiredSearchCV(\n    clf,\n    param_grid,\n    algorithm=\'hba\', # hybrid bat algorithm\n    population_size=50,\n    max_n_gen=100,\n    max_stagnating_gen=10,\n    runs=3,\n    random_state=None, # or any number if you want same results on each run\n)\n\nnia_search.fit(X_train, y_train)\n\n# the best params are stored in nia_search.best_params_\n# finally you can train your model with best params from nia search\nnew_clf = RandomForestClassifier(**nia_search.best_params_, random_state=42)\n```\n\nAlso you plot the search process with _line plot_ or _violin plot_.\n\n```python\nfrom sklearn_nature_inspired_algorithms.helpers import score_by_generation_lineplot, score_by_generation_violinplot\n\n# line plot will plot all of the runs, you can specify the metric to be plotted (\'min\', \'max\', \'median\', \'mean\')\nscore_by_generation_lineplot(nia_search, metric=\'max\')\n\n# in violin plot you need to specify the run to be plotted\nscore_by_generation_violinplot(nia_search, run=0)\n```\n\nJupyter notebooks with full examples are available in [here](examples/notebooks).\n\n### Using a Custom Nature-Inspired Algorithm\n\nIf you do not want to use any of the pre-defined algorithm configurations, you can use any algorithm from the  [NiaPy](https://github.com/NiaOrg/NiaPy) collection.\nThis will allow you to have more control of the algorithm behavior. \nRefer to their [documentation](https://niapy.readthedocs.io/en/latest/) and [examples](https://github.com/NiaOrg/NiaPy/tree/master/examples) for the usage. \n\n__Note:__ Use version >2.x.x of NiaPy package\n\n```python\nfrom niapy.algorithms.basic import GeneticAlgorithm\n\nalgorithm = GeneticAlgorithm() # when custom algorithm is provided random_state is ignored\nalgorithm.set_parameters(NP=50, Ts=5, Mr=0.25)\n\nnia_search = NatureInspiredSearchCV(\n    clf,\n    param_grid,\n    algorithm=algorithm,\n    population_size=50,\n    max_n_gen=100,\n    max_stagnating_gen=20,\n    runs=3,\n)\n\nnia_search.fit(X_train, y_train)\n```\n\n## Contributing \n\nDetailed information on the contribution guidelines are in the [CONTRIBUTING.md](./CONTRIBUTING.md).\n',
    'author': 'Timotej Zatko',
    'author_email': 'timi.zatko@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/timzatko/Sklearn-Nature-Inspired-Algorithms',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<3.11',
}


setup(**setup_kwargs)
