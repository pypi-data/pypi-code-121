# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exhbma']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.1,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'exhbma',
    'version': '0.1.10',
    'description': 'Exhaustive Search with Bayesian Model Averaging',
    'long_description': '# Exhaustive Search with Bayesian Model Averaging (ExhBMA)\n\n# Installation\n```\npip install exhbma\n```\n\n# Documentation\nUser documentation is available [here](https://exhbma.readthedocs.io).\nYou can try sample notebooks in [tutorials](/tutorials) directory.\n\n# Reference paper\nIn preparing.\n',
    'author': 'Koki Obinata',
    'author_email': 'koki.obi.321@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/okada-lab/exhbma',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
