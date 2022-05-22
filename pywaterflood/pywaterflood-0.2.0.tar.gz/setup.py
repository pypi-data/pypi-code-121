# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pywaterflood']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.1.0',
 'numba>=0.55.1',
 'numpy>=1.21',
 'openpyxl>=3.0.9',
 'pandas>=1.0',
 'scipy>=1.4']

extras_require = \
{'devwork': ['jupyterlab>=3.2', 'seaborn>=0.10'],
 'docs': ['sphinx>=4.2.0',
          'sphinx-autoapi>=1.8.4',
          'sphinx-rtd-theme>=1.0',
          'myst-nb>=0.13.1']}

setup_kwargs = {
    'name': 'pywaterflood',
    'version': '0.2.0',
    'description': 'Physics-inspired waterflood performance modeling',
    'long_description': '# `pywaterflood`: Waterflood Connectivity Analysis\n\n[![PyPI version](https://badge.fury.io/py/pywaterflood.svg)](https://badge.fury.io/py/pywaterflood)\n[![Documentation Status](https://readthedocs.org/projects/pywaterflood/badge/?version=latest)](https://pywaterflood.readthedocs.io/en/latest/?badge=latest)\n\n[![License](https://img.shields.io/badge/License-BSD_2--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)\n[![codecov](https://codecov.io/gh/frank1010111/pywaterflood/branch/master/graph/badge.svg?token=3XRGLKO7T8)](https://codecov.io/gh/frank1010111/pywaterflood)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![Python version](https://img.shields.io/badge/Python-3.7%2C%203.8%2C%203.9-blue)](https://www.python.org/downloads/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/pywaterflood)](https://pypi.org/project/pywaterflood/)\n\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/frank1010111/pywaterflood/master?labpath=docs%2Fexample.ipynb)\n\n`pywaterflood` provides tools for capacitance resistance modeling, a\nphysics-inspired model for estimating waterflood performance. It estimates the\nconnectivities and time decays between injectors and producers.\n\n## Overview\n\nA literature review has been written by Holanda, Gildin, Jensen, Lake and Kabir,\nentitled "A State-of-the-Art Literature Review on Capacitance Resistance Models\nfor Reservoir Characterization and Performance Forecasting."\n[They](https://doi.org/10.3390/en11123368) describe CRM as the following:\n\n> The Capacitance Resistance Model (CRM) is a fast way for modeling and\n> simulating gas and waterflooding recovery processes, making it a useful tool\n> for improving flood management in real-time. CRM is an input-output and\n> material balance-based model, and requires only injection and production\n> history, which are the most readily available data gathered throughout the\n> production life of a reservoir.\n\nThere are several CRM versions (see Holanda et al., 2018). Through passing\ndifferent parameters when creating the CRM instance, you can choose between\nCRMIP, where a unique time constant is used for each injector-producer pair, and\nCRMP, where a unique time constant is used for each producer. CRMIP is more\nreliable given sufficient data. With CRMP, you can reduce the number of\nunknowns, which is useful if available production data is limited.\n\n## Getting started\n\nYou can install this package from PyPI with the line\n\n```\npip install pywaterflood\n```\n\n### A simple example\n\n    import pandas as pd\n    from pywaterflood import CRM\n\n    gh_url = "https://raw.githubusercontent.com/frank1010111/pywaterflood/master/testing/data/"\n    prod = pd.read_csv(gh_url + \'production.csv\', header=None).values\n    inj = pd.read_csv(gh_url + "injection.csv", header=None).values\n    time = pd.read_csv(gh_url + "time.csv", header=None).values[:,0]\n\n    crm = CRM(tau_selection=\'per-pair\', constraints=\'up-to one\')\n    crm.fit(prod, inj, time)\n    q_hat = crm.predict()\n    residuals = crm.residual()\n',
    'author': 'Frank Male',
    'author_email': 'frmale@utexas.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/frank1010111/pywaterflood',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
