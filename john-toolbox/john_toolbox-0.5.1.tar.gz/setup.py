# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['john_toolbox',
 'john_toolbox.evaluation',
 'john_toolbox.preprocessing',
 'john_toolbox.tutorial.binary.xgboost',
 'john_toolbox.utils']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.0,<3.0.0',
 'MarkupSafe==2.0.1',
 'numpy>=1.19,<2.0',
 'pandas>=1.1,<2.0',
 'tqdm>=4.51,<5.0']

setup_kwargs = {
    'name': 'john-toolbox',
    'version': '0.5.1',
    'description': 'Wrapper for transformers scikit learn pipeline and wrapper for ml model',
    'long_description': '<h1 align="center">\n\nWelcome to john_toolbox 👋\n\n</h1>\n\n\n![Version](https://img.shields.io/badge/version-0.5.1-blue.svg?cacheSeconds=2592000)\n[![Documentation](https://img.shields.io/badge/documentation-yes-brightgreen.svg)](https://nguyenanht.github.io/john-toolbox/)\n![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)\n![Licence](https://img.shields.io/badge/License-MIT-FFB600.svg) ![Total-lines](https://tokei.rs/b1/github/nguyenanht/john-toolbox)\n[![Downloads](https://static.pepy.tech/personalized-badge/john-toolbox?period=month&units=international_system&left_color=grey&right_color=red&left_text=Downloads/Month)](https://pepy.tech/project/john-toolbox)\n[![Downloads](https://static.pepy.tech/personalized-badge/john-toolbox?period=total&units=international_system&left_color=grey&right_color=red&left_text=Downloads/Total)](https://pepy.tech/project/john-toolbox)\n\n[![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://github.com/scikit-learn/scikit-learn)\n[![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)](https://github.com/pandas-dev/pandas)\n[![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)](https://github.com/numpy/numpy)\n[![Poetry](https://img.shields.io/badge/poetry-%233B82F6.svg?style=for-the-badge&logo=poetry&logoColor=white)](https://github.com/python-poetry/poetry)\n[![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)](https://github.com/pytorch/pytorch)\n\n> This is my own toolbox to handle preprocessing production ready based on scikit-learn Pipeline but with more flexibility.\n### 🏠 [Homepage](https://github.com/nguyenanht/john-toolbox)\n\n## Install\n```sh\npip install john-toolbox\n\n```\n\n\n\n## Author\n👤 **Johnathan Nguyen**\n\n\n* GitHub: [@nguyenanht](https://github.com/{github_username})\n\n## How to use ?\n\nIf you want examples. please refer to [notebooks directory](https://github.com/nguyenanht/john-toolbox/tree/develop/notebooks). It contains tutorials on how to use the package and other useful tutorials to handle end to end machine learning project.\n\n\n\n## Show your support\nGive a ⭐️ if this project helped you!\n\n\n## Useful link\n\n#### how to publish new version in pypi with poetry ?\nhttps://johnfraney.ca/posts/2019/05/28/create-publish-python-package-poetry/\n\n#### how to create a new release ?\nhttps://www.atlassian.com/fr/git/tutorials/comparing-workflows/gitflow-workflow\n\n#### how to generate docs\nhttps://github.com/JamesALeedham/Sphinx-Autosummary-Recursion\n\n#### how to deploy with github actions\nhttps://blog.flozz.fr/2020/09/21/deployer-automatiquement-sur-github-pages-avec-github-actions/\n\n---\n_This README was created with the [markdown-readme-generator](https://github.com/pedroermarinho/markdown-readme-generator)_',
    'author': 'john',
    'author_email': 'contact@nguyenjohnathan.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/nguyenanht/john-toolbox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
