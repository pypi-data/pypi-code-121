# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pandaslearn']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.25',
 'alembic>=1.7.3',
 'backports.weakref>=1.0.post1',
 'backports.zoneinfo>=0.2.1',
 'catboost>=0.26',
 'category-encoders>=2.2.2',
 'fastapi>=0.68.1',
 'joblib>=1.0.1',
 'lightgbm>=3.2.1',
 'loguru>=0.5.3',
 'missingno>=0.5.0',
 'optuna>=2.9.1',
 'pandas-profiling>=3.0.0',
 'pandas-ta>=0.3.2-beta.0',
 'pandas>=1.2.5',
 'pdpipe>=0.0.53',
 'plotnine>=0.8.0',
 'psycopg2>=2.9.1',
 'pydantic>=1.8.2',
 'scikit-learn>=1.0',
 'scikit-lego>=0.6.7',
 'sqlmodel>=0.0.4',
 'stackprinter>=0.2.5',
 'streamlit',
 'streamlit-pandas-profiling>=0.1.2',
 'xgboost>=1.4.2',
 'yellowbrick>=1.3.post1']

setup_kwargs = {
    'name': 'pandaslearn',
    'version': '0.1.9',
    'description': '`pandaslearn` is a small wrapper on top of `scikit-learn` to automate common modeling tasks.',
    'long_description': "# pandaslearn\n\n`pandaslearn` is a small wrapper on top of `scikit-learn` to automate common modeling tasks.\n\n* Create `Trainer` instance with `Dataset` and `Model` instances, `__init__()` in `Trainer` instance should populate `Dataset` and `Model` instance's `logger` attributes. Methods on `Dataset` and `Model` should be called after that, so that everything gets logged appropriately.\n# TODO\n\n* TODO: visualization: add barcharts (plotnine)\n* TODO: visualization: add histograms (plotnine)\n* TODO: visualization: add scatterplots (plotnine)\n* TODO: visualization: add lineplots (plotnine)\n* TODO: visualization: add boxplots (plotnine)\n* TODO: visualization: add violin plots (plotnine)\n* TODO: visualization: add function to change theme (xkcd, ?)\n* TODO: add a `geo` namespace (+ feature engineering, plots)\n* TODO: add tests against a few standard fixtures (precompute values and test against them)\n* TODO: integrate missingno package: functions to only compute/sort nullity\n* TODO: integrate missingno package: plotnine functions matching missingno plot(including geo)\n* TODO: integrate missingno package: timeseries nullity plots (just plot all timelines with gaps)\n* TODO: pandas-profiling has a lot of useful analysis useful for ml. Integrate those (provide textual outcomes like dicts or dfs instead of plot)\n* TODO: future integration targets: https://compose.alteryx.com/en/stable/\n* TODO: future integration targets: https://featuretools.alteryx.com/en/stable/\n* TODO: future integration targets: https://evalml.alteryx.com/en/stable/\n",
    'author': 'Soumendra Prasad Dhanee',
    'author_email': 'soumendra@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/soumendra/pandaslearn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
