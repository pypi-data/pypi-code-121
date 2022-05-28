# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stglance', 'stglance.tests']

package_data = \
{'': ['*']}

install_requires = \
['backports.weakref>=1.0.post1',
 'backports.zoneinfo>=0.2.1',
 'catboost>=0.26',
 'category-encoders>=2.2.2',
 'joblib>=1.0.1',
 'lightgbm>=3.2.1',
 'loguru>=0.5.3',
 'missingno>=0.5.0',
 'pandas-profiling>=3.0.0',
 'pandas-ta>=0.3.2-beta.0',
 'pandas>=1.2.5',
 'pdpipe>=0.0.53',
 'plotnine>=0.8.0',
 'pydantic>=1.8.2',
 'scikit-learn>=1.0',
 'scikit-lego>=0.6.7',
 'stackprinter>=0.2.5',
 'streamlit',
 'streamlit-pandas-profiling>=0.1.2',
 'xgboost>=1.4.2',
 'yellowbrick>=1.3.post1']

setup_kwargs = {
    'name': 'stglance',
    'version': '0.1.4',
    'description': 'stglance is a small collection of streamlit widgets (for machine learning) that you can include in your streamlit app.',
    'long_description': '# stglance\n\n`stglance` is a small collection of `streamlit` widgets that you can include in your streamlit app.\n\n\n## Setting up for development\n\n1. `poetry install`\n2. `poetry run pre-commit autoupdate`\n',
    'author': 'Soumendra Prasad Dhanee',
    'author_email': 'soumendra@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/soumendra/stglance',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
